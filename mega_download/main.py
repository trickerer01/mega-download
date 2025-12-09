# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import itertools
import pathlib
import sys
from asyncio import get_running_loop, run, sleep
from collections.abc import Iterable, Sequence
from contextlib import AsyncExitStack

from aiohttp import ClientTimeout

from .api import DownloadMode, DownloadParamsCallback, FileSystemCallback, Mega, MegaNZError, MegaOptions
from .cmdargs import HelpPrintExitException, prepare_arglist
from .config import BaseConfigContainer, Config
from .defs import (
    CONNECT_RETRIES_BASE,
    CONNECT_TIMEOUT_BASE,
    CONNECT_TIMEOUT_SOCKET_READ,
    MAX_JOBS_DEFAULT,
    MIN_PYTHON_VERSION,
    MIN_PYTHON_VERSION_STR,
    SCAN_CANCEL_KEYCOUNT,
    SCAN_CANCEL_KEYSTROKE,
    LoggingFlags,
)
from .filters import FileExtFilter, FileNameFilter, FileSizeFilter
from .hooks import create_callbacks
from .input import wait_for_key
from .logger import Log
from .version import APP_NAME, APP_VERSION

__all__ = ('MegaDownloader', 'main_async', 'main_sync')


def at_startup() -> None:
    """Inits logger. Reports python version and run options"""
    argv_set = set(sys.argv)
    if argv_set.intersection({'--disable-log-colors', '-g'}):
        Config.nocolors = True
    Log.init()
    if argv_set.intersection({'--version', '--help'}):
        return
    Log.debug(f'Python {sys.version}\n{APP_NAME} ver {APP_VERSION}\nCommand-line args: {" ".join(sys.argv)}')


def make_mega_options(
    before_download_callbacks: Iterable[DownloadParamsCallback] = (),
    after_scan_callbacks: Iterable[FileSystemCallback] = (),
) -> MegaOptions:
    options = MegaOptions(
        dest_base=Config.dest_base,
        retries=Config.retries,
        max_jobs=Config.max_jobs,
        timeout=Config.timeout,
        nodelay=Config.nodelay,
        proxy=Config.proxy,
        extra_headers=Config.extra_headers,
        extra_cookies=Config.extra_cookies,
        filters=(
            *((FileSizeFilter(Config.filter_filesize),) if Config.filter_filesize else ()),
            *((FileNameFilter(Config.filter_filename),) if Config.filter_filename else ()),
            *((FileExtFilter(Config.filter_extensions),) if Config.filter_extensions else ()),
        ),
        download_mode=DownloadMode(Config.download_mode),
        hooks_before_download=tuple(before_download_callbacks),
        hooks_after_scan=tuple(after_scan_callbacks),
        logger=Log,
    )
    return options


class MegaDownloader:
    _client_timeout_default = ClientTimeout(
        total=None, connect=CONNECT_TIMEOUT_BASE, sock_connect=CONNECT_TIMEOUT_BASE, sock_read=float(CONNECT_TIMEOUT_SOCKET_READ),
    )

    def __init__(self, links: list[str], base_config: BaseConfigContainer) -> None:
        self._links = links
        self._config = base_config

    async def run(self) -> list[pathlib.Path]:
        Config.links = self._links or []
        Config.dest_base = self._config.dest_base
        Config.max_jobs = self._config.max_jobs or MAX_JOBS_DEFAULT
        Config.proxy = self._config.proxy or ''
        Config.timeout = self._config.timeout or MegaDownloader._client_timeout_default
        Config.retries = self._config.retries or CONNECT_RETRIES_BASE
        Config.extra_headers = self._config.extra_headers or []
        Config.extra_cookies = self._config.extra_cookies or []
        Config.download_mode = self._config.download_mode or DownloadMode.FULL.value
        Config.logging_flags = self._config.logging_flags or LoggingFlags.INFO.value
        Config.filter_filesize = self._config.filter_filesize
        Config.filter_filename = self._config.filter_filename
        Config.filter_extensions = self._config.filter_extensions
        Config.nocolors = self._config.nocolors or False
        Config.nodelay = self._config.nodelay or False

        if not Config.links:
            Log.error('Nothing to process, aborted')
            return []
        before_download_callbacks, after_scan_callbacks = create_callbacks()
        mega = Mega(make_mega_options(before_download_callbacks, after_scan_callbacks))
        abort_waiter = get_running_loop().create_task(wait_for_key(SCAN_CANCEL_KEYSTROKE, SCAN_CANCEL_KEYCOUNT, mega.abort))

        async with AsyncExitStack() as ctx:
            await ctx.enter_async_context(mega)
            [await ctx.enter_async_context(_) for _ in before_download_callbacks]
            [await ctx.enter_async_context(_) for _ in after_scan_callbacks]
            results = [await mega.download_url(_) for _ in Config.links]
        abort_waiter.cancel()
        await abort_waiter

        return list(itertools.chain(*results))


async def main(args: Sequence[str]) -> int:
    try:
        prepare_arglist(args)
    except HelpPrintExitException:
        return 0

    try:
        mega = MegaDownloader(Config.links, Config)
        results = await mega.run()
        Log.info('\n'.join(('\n', *(_.name for _ in results))) or '\nNothing')
        return 0
    except MegaNZError:
        import traceback
        Log.fatal(f'Catched MegaNZError!\n{traceback.format_exc()}')
        return -2
    except Exception as e:
        import traceback
        Log.fatal(f'Unhandled exception {e.__class__.__name__}!\n{traceback.format_exc()}')
        return -3


async def run_main(args: Sequence[str]) -> int:
    res = await main(args)
    await sleep(0.5)
    return res


async def main_async(args: Sequence[str]) -> int:
    assert sys.version_info >= MIN_PYTHON_VERSION, f'Minimum python version required is {MIN_PYTHON_VERSION_STR}!'
    try:
        return await run_main(args)
    except (KeyboardInterrupt, SystemExit):
        Log.warn('Warning: catched KeyboardInterrupt/SystemExit...')
        return -1


def main_sync(args: Sequence[str]) -> int:
    at_startup()
    try:
        loop = get_running_loop()
    except RuntimeError:  # no current event loop
        loop = None
    run_func = loop.run_until_complete if loop else run
    return run_func(main_async(args))


if __name__ == '__main__':
    exit(main_sync(sys.argv[1:]))

#
#
#########################################
