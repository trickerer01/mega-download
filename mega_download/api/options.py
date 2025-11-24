# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from typing import TypedDict

from aiohttp import ClientTimeout

from .defs import DownloadMode
from .filters import Filter
from .logging import Logger


class MegaOptions(TypedDict):
    # for local
    dest_base: str
    retries: int
    timeout: ClientTimeout
    proxy: str
    extra_headers: list[tuple[str, str]]
    extra_cookies: list[tuple[str, str]]
    filters: tuple[Filter, ...]
    download_mode: DownloadMode
    # for global
    logger: Logger

#
#
#########################################
