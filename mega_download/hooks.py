# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from __future__ import annotations

import json
import pathlib
import sys
from contextlib import AbstractAsyncContextManager

from .api import SITE_PRIMARY, DownloadParams, DownloadParamsDump
from .config import Config
from .defs import SLASH, UTF8
from .logger import Log
from .util import datetime_str_nfull

__all__ = ('create_before_download_callbacks',)


class PathJSONEncode(json.JSONEncoder):
    def default(self, o: pathlib.Path) -> str:
        return o.as_posix()


class Callback(AbstractAsyncContextManager):
    def execute(self, url: str, download_params: DownloadParams) -> None: ...
    def __str__(self) -> str: ...


class DumpLinksCallback(Callback):
    def __init__(self, filename_base: str) -> None:
        super().__init__()
        self._filepath = pathlib.Path(Config.dest_base) / f'{filename_base}.json'
        self._json: DownloadParamsDump = {
            'args': ' '.join(sys.argv[1:]),
        }

    async def __aenter__(self) -> DumpLinksCallback:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        Log.info(f'[{self.__class__.__name__}] Saving to {self._filepath}')
        with open(self._filepath, 'wt', encoding=UTF8) as outfile:
            json.dump(self._json, outfile, ensure_ascii=False, indent=4, cls=PathJSONEncode)

    def execute(self, url: str, download_params: DownloadParams) -> None:
        if url not in self._json:
            self._json[url] = []
        self._json[url].append(DownloadParams(
            index=download_params['index'],
            direct_file_url=download_params['direct_file_url'],
            output_path=download_params['output_path'].relative_to(Config.dest_base),
            file_size=download_params['file_size'],
            iv=download_params['iv'],
            meta_mac=download_params['meta_mac'],
            k_decrypted=download_params['k_decrypted'],
        ))

    def __str__(self) -> str:
        return f'DumpLinksCallback\n{json.dumps(self._json, ensure_ascii=False, indent=4)}'


def create_before_download_callbacks() -> set[Callback]:
    filename_base = f'mega{Config.links[0].replace(SITE_PRIMARY, "").replace(SLASH, "_") if Config.links else ""}_{datetime_str_nfull()}'
    callbacks = set[Callback]()
    if Config.dump_links:
        callbacks.add(DumpLinksCallback(filename_base))
    return callbacks

#
#
#########################################
