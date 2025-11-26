# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import pathlib
from typing import TypedDict

from aiohttp import ClientTimeout

from .defs import DownloadMode
from .filters import Filter
from .hooks import DownloadParamsCallback
from .logging import Logger


class MegaOptions(TypedDict):
    # for local
    dest_base: pathlib.Path
    retries: int
    max_jobs: int
    timeout: ClientTimeout
    nodelay: bool
    proxy: str
    extra_headers: list[tuple[str, str]]
    extra_cookies: list[tuple[str, str]]
    filters: tuple[Filter, ...]
    hooks_before_download: tuple[DownloadParamsCallback]
    download_mode: DownloadMode
    # for global
    logger: Logger

#
#
#########################################
