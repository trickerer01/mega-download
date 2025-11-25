# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from __future__ import annotations

import pathlib
import random
import re
from asyncio import gather, sleep
from collections.abc import Sequence
from typing import TypeAlias

from aiofile import async_open
from aiohttp import ClientConnectorError, ClientResponse, ClientResponseError, ClientSession, ClientTimeout, TCPConnector
from aiohttp_socks import ProxyConnector

from mega_download.util.strings import ensure_scheme_https
from mega_download.util.useragent import UAManager

from .chunkgen import make_chunk_decryptor, make_chunk_generator
from .containers import (
    DownloadParams,
    File,
    Folder,
    IntVector,
    NodeType,
    ParsedUrl,
    SharedKey,
    SharedkeysDict,
    UserInfo,
)
from .defs import CONNECT_RETRY_DELAY, MAX_QUEUE_SIZE, SITE_API, UINT32_MAX, DownloadMode, Mem
from .encryption import (
    base64_to_ints,
    base64_url_decode,
    base64_url_encode,
    decrypt_attr,
    decrypt_key,
    encrypt_key,
    ints_to_base64,
    make_hashcash_token,
    pack_sequence,
    unpack_sequence,
    urand,
)
from .exceptions import LoginError, MegaErrorCodes, RequestError, ValidationError
from .filters import Filter, any_filter_matching
from .logging import Log, set_logger
from .options import MegaOptions

__all__ = ('Mega',)

APIResponse: TypeAlias = File | Folder | UserInfo | str | int

re_mega_file_id_v1 = re.compile(r'/#!(.*)')
re_mega_file_id_v2 = re.compile(r'\W(\w{8})\W')
re_mega_folder_file_id = re.compile(r'\W\w{4}\W(\w{8})')


class Mega:
    def __init__(self, options: MegaOptions) -> None:
        # globals
        set_logger(options['logger'])
        # locals
        self._aborted = False
        self._session: ClientSession | None = None
        self._sequence_num: int = urand()
        self._sid: str = ''
        self._user_nodes: dict[NodeType, str] = {}
        self._master_key: IntVector = ()
        self._shared_keys: SharedkeysDict = {}
        self._queue_size: int = 0
        self._parsed: ParsedUrl = ParsedUrl.default()
        # options
        self._dest_base: str = options['dest_base']
        self._retries: int = options['retries']
        self._timeout: ClientTimeout = options['timeout']
        self._proxy: str = options['proxy']
        self._extra_headers: list[tuple[str, str]] = options['extra_headers']
        self._extra_cookies: list[tuple[str, str]] = options['extra_cookies']
        self._filters: tuple[Filter, ...] = options['filters']
        self._download_mode = options['download_mode']
        # ensure correct args
        assert Log
        assert self._dest_base
        assert isinstance(self._download_mode, DownloadMode)
        _ = self._download_mode

    async def __aenter__(self) -> Mega:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def _make_session(self) -> ClientSession:
        if self._session is not None:
            raise ValidationError('make_session should only be called once!')
        use_proxy = bool(self._proxy)
        if use_proxy:
            connector = ProxyConnector.from_url(self._proxy, limit=MAX_QUEUE_SIZE)
        else:
            connector = TCPConnector(limit=MAX_QUEUE_SIZE)
        session = ClientSession(connector=connector, read_bufsize=Mem.MB, timeout=self._timeout)
        new_useragent = UAManager.select_useragent(self._proxy if use_proxy else None)
        Log.trace(f'[{"P" if use_proxy else "NP"}] Selected user-agent \'{new_useragent}\'...')
        session.headers.update({'User-Agent': new_useragent, 'Content-Type': 'application/json'})
        if self._extra_headers:
            for hk, hv in self._extra_headers:
                session.headers.update({hk: hv})
        if self._extra_cookies:
            for ck, cv in self._extra_cookies:
                session.cookie_jar.update_cookies({ck: cv})
        return session

    async def query_api(self, data_input: list[dict[str, str]], *, add_params: dict[str, str] | None = None) -> APIResponse:
        if self._session is None:
            self._session = self._make_session()

        def handle_int_resp(int_resp: int) -> int:
            if int_resp == 0:
                return int_resp
            if int_resp == MegaErrorCodes.EAGAIN:
                raise ConnectionError('Request failed, retrying')
            raise RequestError(int_resp)

        extra_params: dict[str, str] = add_params or {}

        retries = 0
        response: ClientResponse | None = None
        while retries <= self._retries:
            response = None
            try:
                params: dict[str, int | str] = {'id': self._sequence_num} | extra_params
                self._sequence_num = (self._sequence_num + 1) % UINT32_MAX

                if self._sid:
                    params['sid'] = self._sid

                Log.trace(f'Sending API request: POST, params: {params!s}, input: {data_input!s}')
                response = await self._session.post(SITE_API, params=params, json=data_input)

                hashcash_challenge: str = response.headers.get('X-Hashcash')
                if hashcash_challenge:
                    hashcash_token = make_hashcash_token(hashcash_challenge)
                    Log.info(f'Solving xhashcash login challenge..., Body: {hashcash_challenge} -> {hashcash_token}')
                    response = await self._session.post(SITE_API, params=params, json=data_input, headers={'X-Hashcash': hashcash_token})
                    if hashcash_challenge := response.headers.get('X-Hashcash'):
                        raise RequestError(f'Login failed. Mega requested a proof of work with xhashcash: {hashcash_challenge}')

                jresp: list[int] | list[str] | int = await response.json()

                if isinstance(jresp, int):
                    return handle_int_resp(jresp)
                elif not isinstance(jresp, list):
                    raise RequestError(f'Unknown response: {jresp!r}')
                elif jresp:
                    first_element = jresp[0]
                    if isinstance(first_element, int):
                        return handle_int_resp(first_element)
                    return first_element
                else:
                    raise RequestError(f'Unknown response: {jresp!r}')
            except Exception as e:
                if response is not None and '404.' in str(response.url):
                    Log.error('ERROR: 404')
                    assert False
                else:
                    Log.error(f'[{retries + 1:d}] fetch_html exception status '
                              f'{f"{response.status:d}" if response is not None else "???"}: '
                              f'\'{e.message if isinstance(e, ClientResponseError) else str(e)}\'')
                if isinstance(e, RequestError):
                    raise
                if not isinstance(e, ClientConnectorError):
                    retries += 1
                if self._aborted:
                    return 0
                if retries <= self._retries:
                    await sleep(random.uniform(*CONNECT_RETRY_DELAY))
                continue

        if retries > self._retries:
            Log.error('Unable to connect. Aborting')
        elif response is None:
            Log.error('ERROR: Failed to receive any data')
        raise ConnectionError

    async def _login(self) -> None:
        Log.info('Logging in as anonymous...')
        master_key = [urand()] * 4
        password_key = [urand()] * 4
        self_challenge = [urand()] * 4

        user: str = await self.query_api([{
            'a': 'up',
            'k': ints_to_base64(encrypt_key(master_key, password_key)),
            'ts': base64_url_encode(pack_sequence(self_challenge) + pack_sequence(encrypt_key(self_challenge, master_key))),
        }])

        resp: UserInfo = await self.query_api([{'a': 'us', 'user': user}])
        master_key_encrypted = base64_to_ints(resp['k'])
        self._master_key = decrypt_key(master_key_encrypted, password_key)
        if b64_tsid := resp.get('tsid'):
            tsid = base64_url_decode(b64_tsid)
            key_encrypted = pack_sequence(encrypt_key(unpack_sequence(tsid[:16]), self._master_key))
            Log.trace(f'Key (encrypted): {key_encrypted}')
            if key_encrypted == tsid[-16:]:
                self._sid = b64_tsid
        else:
            b64_csid = resp.get('csid', 'UNK')
            raise LoginError(f'Fatal: login response does not contain \'tsid\' key. csid: \'{b64_csid}\'!')

    async def _get_nodes(self) -> list[File | Folder]:
        folder: Folder = await self.query_api([{'a': 'f', 'c': 1, 'r': 1}])
        self._shared_keys = self._init_shared_keys(folder, self._master_key)
        nodes: list[File | Folder] = []
        for _, node in enumerate(folder['f'], 1):
            pnode = self._process_node(node)
            nodes.append(pnode)
        return nodes

    async def _get_nodes_in_shared_folder(self, folder_id: str) -> list[File | Folder]:
        folder: Folder = await self.query_api([{'a': 'f', 'c': 1, 'ca': 1, 'r': 1}], add_params={'n': folder_id})
        nodes: list[File | Folder] = []
        for _, node in enumerate(folder['f'], 1):
            pnode = self._process_node(node)
            nodes.append(pnode)
        return nodes

    async def _prepare_nodes(self, folder_id: str, shared_key: Sequence[int]) -> list[File | Folder]:
        nodes: list[File | Folder] = []
        for file_or_folder in await self._get_nodes_in_shared_folder(folder_id):
            encrypted_key = base64_to_ints(file_or_folder['k'].split(':')[1])
            key = decrypt_key(encrypted_key, shared_key)
            if file_or_folder['t'] == NodeType.FILE:
                k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
            elif file_or_folder['t'] == NodeType.FOLDER:
                k = key
            else:
                assert False, f'Unhandled node type {file_or_folder["t"]} found in folder {folder_id}!'

            iv = (*key[4:6], 0, 0)
            meta_mac = key[6:8]

            attrs = decrypt_attr(base64_url_decode(file_or_folder['a']), k)
            file_or_folder['attributes'] = attrs
            file_or_folder['k_decrypted'] = k
            file_or_folder['iv'] = iv
            file_or_folder['meta_mac'] = meta_mac
            nodes.append(file_or_folder)
        return nodes

    def _process_node(self, file_or_folder: File | Folder) -> File | Folder:
        Log.trace(f'Node {file_or_folder["p"]}/{file_or_folder["h"]}...')
        if file_or_folder['t'] == NodeType.FILE or file_or_folder['t'] == NodeType.FOLDER:
            keys = dict(tuple[str, str](keypart.split(':', 1)) for keypart in file_or_folder['k'].split('/') if ':' in keypart)
            uid: str = file_or_folder['u']
            key: IntVector | None = None
            # user objects
            if uid in keys:
                key = decrypt_key(base64_to_ints(keys[uid]), self._master_key)
            # shared folders
            elif 'su' in file_or_folder and 'sk' in file_or_folder and ':' in file_or_folder['k']:
                Log.trace(f'Processing shared folder {file_or_folder["p"]}/{file_or_folder["h"]}...')
                shared_key = decrypt_key(base64_to_ints(file_or_folder['sk']), self._master_key)
                key = decrypt_key(base64_to_ints(keys[file_or_folder['h']]), shared_key)
                if file_or_folder['su'] not in self._shared_keys:
                    self._shared_keys[file_or_folder['su']] = {}
                self._shared_keys[file_or_folder['su']][file_or_folder['h']] = shared_key
            # shared files
            elif file_or_folder['u'] and file_or_folder['u'] in self._shared_keys:
                Log.trace(f'Processing shared file {file_or_folder["p"]}/{file_or_folder["h"]}...')
                for hkey in self._shared_keys[file_or_folder['u']]:
                    shared_key = self._shared_keys[file_or_folder['u']][hkey]
                    if hkey in keys:
                        key = decrypt_key(base64_to_ints(keys[hkey]), shared_key)
                        break
            if file_or_folder['h'] and file_or_folder['h'] in self._shared_keys.get('EXP', ()):
                shared_key = self._shared_keys['EXP'][file_or_folder['h']]
                encrypted_key = unpack_sequence(base64_url_decode(file_or_folder['k'].split(':')[-1]))
                key = decrypt_key(encrypted_key, shared_key)
                file_or_folder['sk_decrypted'] = shared_key
            if key is not None:
                # file
                if file_or_folder['t'] == NodeType.FILE:
                    # file_or_folder = cast(File, file_or_folder)
                    k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
                    file_or_folder['iv'] = (*key[4:6], 0, 0)
                    file_or_folder['meta_mac'] = key[6:8]
                # folder
                else:
                    k = key
                file_or_folder['key_decrypted'] = key
                file_or_folder['k_decrypted'] = k
                attributes_bytes = base64_url_decode(file_or_folder['a'])
                attributes = decrypt_attr(attributes_bytes, k)
                file_or_folder['attributes'] = attributes
            # other => wrong object
            elif not file_or_folder['k']:
                file_or_folder['attributes'] = {'n': 'Unknown Object'}
        return file_or_folder

    async def download_url(self, url: str) -> tuple[pathlib.Path, ...]:
        self._parsed = self._parse_url(url)
        assert self._parsed.key_b64
        assert self._parsed.folder_id or self._parsed.file_id

        Log.info(f'Processing {"folder" if self._parsed.folder_id else "file"} {self._parsed.folder_id or self._parsed.file_id}...')
        if self._parsed.folder_id and self._parsed.file_id:
            Log.info(f'Pre-selected file {self._parsed.file_id}...')
        await self._login()
        if self._parsed.folder_id:
            return await self._download_folder()
        else:
            return await self._download_file(),  # noqa: COM818

    async def _download_folder_file(self, index: int, folder_id: str, file: File, file_path: pathlib.Path) -> pathlib.Path:
        if self._aborted:
            return file_path
        file_data: File = await self.query_api([{'a': 'g', 'g': 1, 'n': file['h']}], add_params={'n': folder_id})
        file_url = file_data['g']
        file_size = file_data['s']
        download_path = pathlib.Path(self._dest_base) / file_path
        file_url_https = ensure_scheme_https(file_url)
        iv = file['iv']
        meta_mac = file['meta_mac']
        k_decrypted = file['k_decrypted']
        return await self._download(DownloadParams(index, file_url_https, download_path, file_size, iv, meta_mac, k_decrypted))

    async def _download_folder(self) -> tuple[pathlib.Path, ...]:
        fk_arr = base64_to_ints(self._parsed.key_b64)
        fof_nodes: dict[str, File | Folder] = {node['h']: node for node in await self._prepare_nodes(self._parsed.folder_id, fk_arr)}
        Log.trace(f'Folder {self._parsed.folder_id} nodes: {fof_nodes!s}')

        root_id: str = next(iter(fof_nodes))
        root_node: Folder = fof_nodes[root_id]
        ftree: dict[pathlib.PurePosixPath, File | Folder] = await self._build_file_system(fof_nodes, [root_id])
        file_count = len({_ for _ in ftree if ftree[_]['t'] == NodeType.FILE})
        Log.info(f'Folder {self._parsed.folder_id}, root {root_id} \'{root_node["attributes"]["n"]}\': found {file_count:d} files...')

        proc_queue: set[pathlib.PurePosixPath] = self._filter_folder_contents(ftree)
        self._queue_size = len({_ for _ in proc_queue if ftree[_]['t'] == NodeType.FILE})
        Log.info(f'Saving {self._queue_size:d} / {file_count:d} files...')

        tasks = []
        idx = 0
        for path, file_or_folder in ftree.items():
            if self._aborted:
                return ()
            if file_or_folder['t'] != NodeType.FILE:
                Log.trace(f'Skipping non-file node {file_or_folder!s}...')
                continue
            if path not in proc_queue:
                Log.trace(f'Skipping excluded node {file_or_folder!s} ({path})...')
                continue
            tasks.append(self._download_folder_file(idx, self._parsed.folder_id, file_or_folder, pathlib.Path(path)))
            idx += 1

        results: tuple[pathlib.Path | BaseException, ...] = await gather(*tasks)
        Log.info(f'Downloaded {len([c for c in results if isinstance(c, pathlib.Path)])} / {len(tasks)} files')
        return results

    async def _download_file(self) -> pathlib.Path:
        fk_arr = base64_to_ints(self._parsed.key_b64)
        file: File = await self.query_api([{'a': 'g', 'g': 1, 'p': self._parsed.file_id}])
        k = (fk_arr[0] ^ fk_arr[4], fk_arr[1] ^ fk_arr[5], fk_arr[2] ^ fk_arr[6], fk_arr[3] ^ fk_arr[7])
        iv = (*fk_arr[4:6], 0, 0)
        meta_mac = fk_arr[6:8]

        # Seems to happens sometimes... When this occurs, files are
        # inaccessible also in the official web app.
        # Strangely, files can come back later.
        if 'g' not in file:
            raise RequestError('File not accessible anymore')

        file_url = file['g']
        file_size = file['s']
        attribs_bytes = base64_url_decode(file['at'])
        attribs = decrypt_attr(attribs_bytes, k)
        file_name: str = attribs['n']
        self._queue_size = 1

        file_url_https = ensure_scheme_https(file_url)
        dest_base = pathlib.Path(*((self._dest_base,) if isinstance(self._dest_base, str) else ()))
        output_path = dest_base / file_name

        if ffilter := any_filter_matching(file, self._filters):
            Log.info(f'File {file_name} was filtered out by {ffilter!s}. Skipped!')
            return output_path

        return await self._download(DownloadParams(0, file_url_https, output_path, file_size, iv, meta_mac, k))

    async def _download(self, params: DownloadParams) -> pathlib.Path:
        if self._download_mode == DownloadMode.SKIP:
            return params.output_path
        if self._aborted:
            return params.output_path
        assert self._session is not None
        num = params.index + 1
        direct_file_url = params.direct_file_url
        output_path = params.output_path
        file_size = params.file_size
        iv = params.iv
        meta_mac = params.meta_mac
        k_decrypted = params.k_decrypted

        touch = self._download_mode == DownloadMode.TOUCH

        if output_path.exists():
            existing_size = output_path.stat().st_size
            if not (touch and existing_size == 0):
                size_match_msg = f'({"COMPLETE" if existing_size == file_size else "MISMATCH!"})'
                exists_msg = f'{output_path} already exists, size: {existing_size / Mem.MB:.2f} MB {size_match_msg}'
                ans = 'q'
                while ans not in 'yYnN01':
                    ans = input(f'{exists_msg}. Overwrite? [y/N]\n')
                    if ans in 'nN0':
                        Log.warn(f'{output_path.name} was skipped')
                        return output_path
                    else:
                        Log.warn(f'Overwriting {output_path.name}...')

        touch_msg = ' <touch>' if touch else ''
        size_msg = '0.0 / ' if touch else ''
        Log.info(f'Saving{touch_msg} {output_path.name} => {output_path} ({size_msg}{file_size / Mem.MB:.2f} MB)...')

        output_path.parent.mkdir(parents=True, exist_ok=True)
        chunk_generator = make_chunk_generator(file_size)
        chunk_decryptor = make_chunk_decryptor(iv, k_decrypted, meta_mac)
        _ = next(chunk_decryptor)  # Init chunk decryptor

        async with async_open(output_path, 'wb') as output_file:
            if not touch:
                bytes_written = 0
                async with self._session.get(direct_file_url) as response:
                    for i, chunk in enumerate(chunk_generator):
                        if self._aborted:
                            break
                        raw_chunk: bytes = await response.content.readexactly(chunk.size)
                        decrypted_chunk: bytes = chunk_decryptor.send(raw_chunk)
                        actual_size = len(decrypted_chunk)
                        bytes_written += actual_size
                        dwn_progress_str = f'+{actual_size:d} ({bytes_written / Mem.MB:.2f} / {file_size / Mem.MB:.2f} MB)'
                        Log.info(f'[{num:d} / {self._queue_size:d}] {output_path.name} chunk {i + 1:d}: {dwn_progress_str}...')
                        await output_file.write(decrypted_chunk)
        try:
            if self._aborted or touch:
                chunk_decryptor.close()
            else:
                # Finalize decryptor (trigger integrity check)
                chunk_decryptor.send(None)
        except StopIteration:
            pass

        if output_path.exists():
            total_size = output_path.stat().st_size
            Log.info(f'{output_path.name} {"" if total_size == file_size else "NOT "}completed ({total_size / Mem.MB:.2f} MB)')
            return output_path

        Log.error(f'FAILED to download {output_path.name}!')
        return pathlib.Path()

    def _filter_folder_contents(self, ftree: dict[pathlib.PurePosixPath, File | Folder]) -> set[pathlib.PurePosixPath]:
        proc_queue = set[pathlib.PurePosixPath]()
        file_idx = 0
        enqueued_idx = 0
        for qpath, node in ftree.items():
            if self._aborted:
                break
            do_append = node['t'] != NodeType.FILE
            if not do_append:
                # is file
                file_idx += 1
                file: File = node
                if self._parsed.folder_id and self._parsed.file_id:
                    file_id = file['h']
                    do_append = file_id == self._parsed.file_id
                    if not do_append:
                        Log.trace(f'[{file_idx:d}] File \'{file_id}\' is not selected for download, skipped...')
                        continue
                elif self._filters:
                    if ffilter := any_filter_matching(file, self._filters):
                        file_name = file['attributes']['n']
                        Log.info(f'[{file_idx:d}] File {file_name} was filtered out by {ffilter!s}. Skipped!')
                        continue
                    do_append = True
                else:
                    file_size = file['s']
                    ans = 'q'
                    while ans not in 'nNyY10':
                        ans = input(f'[{file_idx:d}] Download {qpath.name} ({file_size / Mem.MB:.2f} MB)? [Y/n]\n')
                    do_append = ans in 'yY1'
            if do_append:
                if ftree[qpath]['t'] == NodeType.FILE:
                    enqueued_idx += 1
                    Log.info(f'[{enqueued_idx:d}] {qpath.name} enqueued...')
                proc_queue.add(qpath)
        return proc_queue

    @staticmethod
    def _parse_url(url: str) -> ParsedUrl:
        folder_lookup1, folder_lookup2 = '/folder/', '#F!'
        file_lookup1, file_lookup2 = '/file/', '!'
        has_folder1, has_folder2 = folder_lookup1 in url, folder_lookup2 in url
        has_file1, has_file2 = file_lookup1 in url, file_lookup2 in url
        root_folder_id = file_id = shared_key = ''
        if has_folder1 or has_folder2:
            if has_folder1:
                parts = url.split(folder_lookup1, 1)[1]
                if has_file1:
                    assert url.index(folder_lookup1) < url.index(file_lookup1), f'Unsupported folder file link format \'{url}\'!'
                    parts = parts.split('/', 1)[0]
                    ffmatch = re_mega_folder_file_id.search(url)
                    assert ffmatch, f'Unable to parse folder url: folder file id not found in \'{url}\'!'
                    file_id = ffmatch.group(1)
            elif has_folder2:
                parts = url.split(folder_lookup2, 1)[1]
            else:
                raise ValueError(f'Not a valid folder URL {url}')
            root_folder_id, shared_key = tuple(parts.split('#', 1))
        elif has_file1 or has_file2:
            if has_file1:
                # V2 URL structure
                # ex: https://mega.nz/file/cH51DYDR#qH7QOfRcM-7N9riZWdSjsRq
                url = url.replace(' ', '')
                fmatch_v2 = re_mega_file_id_v2.search(url)
                assert fmatch_v2, f'Unable to parse url v2: file id not found in \'{url}\'!'
                file_id = fmatch_v2.group(1)
                shared_key = url[fmatch_v2.end():]
            elif has_file2:
                # V1 URL structure
                # ex: https://mega.nz/#!Ue5VRSIQ!kC2E4a4JwfWWCWYNJovGFHlbz8F
                fmatch_v1 = re_mega_file_id_v1.search(url)
                assert fmatch_v1, f'Unable to parse url v1: file id not found in \'{url}\'!'
                file_id = fmatch_v1.group(1)
                shared_key = file_id  # yes
            else:
                raise ValueError(f'Not a valid file URL {url}')
        return ParsedUrl(folder_id=root_folder_id, file_id=file_id, key_b64=shared_key)

    @staticmethod
    def _init_shared_keys(folder: Folder, master_key: Sequence[int]) -> SharedkeysDict:
        shared_key: SharedKey = {}
        for ok_item in folder['ok']:
            decrypted_shared_key = decrypt_key(base64_to_ints(ok_item['k']), master_key)
            shared_key[ok_item['h']] = decrypted_shared_key
        shared_keys: SharedkeysDict = {}
        for s_item in folder['s']:
            if s_item['u'] not in shared_keys:
                shared_keys[s_item['u']] = {}
            if s_item['h'] in shared_key:
                shared_keys[s_item['u']][s_item['h']] = shared_key[s_item['h']]
        return shared_keys

    @staticmethod
    async def _build_file_system(node_map: dict[str, File | Folder], root_ids: list[str]) -> dict[pathlib.PurePosixPath, File | Folder]:
        async def build_path_tree(parent_item_id: str, parent_item_path: pathlib.PurePosixPath) -> None:
            for child_item in parent_mapping.get(parent_item_id, []):
                item_name: str = child_item['attributes'].get('n')
                if item_name:
                    item_path = parent_item_path / item_name
                    path_mapping[item_path] = child_item
                    if child_item['t'] == NodeType.FOLDER:
                        await build_path_tree(child_item['h'], item_path)

        path_mapping: dict[pathlib.PurePosixPath, File | Folder] = {}
        parent_mapping: dict[str, list[File | Folder]] = {}  # parent_id -> child nodes

        for file_or_folder_node in node_map.values():
            parent_id = file_or_folder_node['p']
            if parent_id not in parent_mapping:
                parent_mapping[parent_id] = []
            parent_mapping[parent_id].append(file_or_folder_node)

        for root_id in root_ids:
            root_node = node_map[root_id]
            root_name = root_node['attributes']['n']
            root_path = pathlib.PurePosixPath(root_name if root_name != 'Cloud Drive' else '.')
            path_mapping[root_path] = root_node
            await build_path_tree(root_id, root_path)

        sorted_mapping: dict[pathlib.PurePosixPath, File | Folder] = {k: path_mapping[k] for k in sorted(path_mapping)}
        return sorted_mapping

#
#
#########################################
