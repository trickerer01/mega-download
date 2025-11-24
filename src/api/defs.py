# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import datetime
import os
from enum import IntEnum, StrEnum
from typing import Literal, NamedTuple

MIN_PYTHON_VERSION = (3, 10)
MIN_PYTHON_VERSION_STR = f'{MIN_PYTHON_VERSION[0]:d}.{MIN_PYTHON_VERSION[1]:d}'

CONNECT_RETRIES_BASE = 50
CONNECT_TIMEOUT_BASE = 10
CONNECT_TIMEOUT_SOCKET_READ = 30
CONNECT_REQUEST_DELAY = 0.3
CONNECT_RETRY_DELAY = (4.0, 8.0)

MAX_DEST_SCAN_SUB_DEPTH_DEFAULT = 1
MAX_DEST_SCAN_UPLEVELS_DEFAULT = 0
MAX_VIDEOS_QUEUE_SIZE = 1
MAX_SCAN_QUEUE_SIZE = 1
MAX_QUEUE_SIZE = 1
DOWNLOAD_STATUS_CHECK_TIMER = 60
DOWNLOAD_QUEUE_STALL_CHECK_TIMER = 30
DOWNLOAD_CONTINUE_FILE_CHECK_TIMER = 30

FULLPATH_MAX_BASE_LEN = 240

# API
CHUNK_BLOCK_LEN = 16
EMPTY_IV = b'\0' * CHUNK_BLOCK_LEN
UINT32_MAX = 0xFFFFFFFF
DOWNLOAD_CHUNK_SIZE_INIT = 0x20000
DOWNLOAD_CHUNK_SIZE_MAX = 0x100000

PREFIX = 'mega_'
SLASH = '/'
UTF8 = 'utf-8'
LATIN1 = 'latin-1'
DEFAULT_EXT = ''
HTTPS_PREFIX = 'https://'
START_TIME = datetime.datetime.now()

SITE_PRIMARY = f'{HTTPS_PREFIX}mega.nz'
SITE_API = f'{HTTPS_PREFIX}g.api.mega.co.nz/cs'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Goanna/6.7 Firefox/102.0 PaleMoon/33.3.1'
DEFAULT_HEADERS = {'Content-Type': 'application/json', 'User-Agent': USER_AGENT}


class DownloadMode(StrEnum):
    FULL = 'full'
    TOUCH = 'touch'
    SKIP = 'skip'


DOWNLOAD_MODES: tuple[str, ...] = tuple(_.value for _ in DownloadMode.__members__.values())
'''('full','touch','skip')'''
DOWNLOAD_MODE_DEFAULT = DownloadMode.FULL.value
"""'full'"""


class Quality(str):
    def __init__(self, _: Literal['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p', 'preview', 'unk']) -> ...: ...

    def __lt__(self, other: str) -> bool:
        return QUALITIES.index(self) > QUALITIES.index(other)

    def __gt__(self, other: str) -> bool:
        return QUALITIES.index(self) < QUALITIES.index(other)

    def __le__(self, other: str) -> bool:
        return QUALITIES.index(self) >= QUALITIES.index(other)

    def __ge__(self, other: str) -> bool:
        return QUALITIES.index(self) <= QUALITIES.index(other)


QUALITY_2160P = Quality('2160p')
QUALITY_1440P = Quality('1440p')
QUALITY_1080P = Quality('1080p')
QUALITY_720P = Quality('720p')
QUALITY_480P = Quality('480p')
QUALITY_360P = Quality('360p')
QUALITY_240P = Quality('240p')
QUALITY_144P = Quality('144p')

QUALITIES = (QUALITY_2160P, QUALITY_1080P, QUALITY_720P, QUALITY_480P, QUALITY_360P)

DEFAULT_QUALITY = QUALITY_360P


class NamingFlags:
    NONE = 0x00
    PREFIX = 0x01
    SCORE = 0x02
    TITLE = 0x04
    TAGS = 0x08
    QUALITY = 0x10
    # extra
    USE_URL_TITLE = 0x20
    ALL_DEFAULT = PREFIX | SCORE | TITLE | TAGS | QUALITY
    '''0x1F'''
    ALL_EXTRA = USE_URL_TITLE
    '''0x20'''
    ALL = ALL_DEFAULT | ALL_EXTRA
    '''0x3F'''


NAMING_FLAGS = {
    'none': f'0x{NamingFlags.NONE:02X}',
    'prefix': f'0x{NamingFlags.PREFIX:02X}',
    'score': f'0x{NamingFlags.SCORE:02X}',
    'title': f'0x{NamingFlags.TITLE:02X}',
    'tags': f'0x{NamingFlags.TAGS:02X}',
    'quality': f'0x{NamingFlags.QUALITY:02X}',
    'full': f'0x{NamingFlags.ALL_DEFAULT & ~NamingFlags.PREFIX:02X}',
    'urltitle': f'0x{NamingFlags.USE_URL_TITLE:02X}',
}
'''
{\n\n'none': '0x00',\n\n'prefix': '0x01',\n\n'score': '0x02',\n\n'title': '0x04',\n\n'tags': '0x08',\n\n'quality': '0x10',
\n\n'full': '0x1F'\n\n'urltitle': '0x20'\n\n}
'''
NAMING_FLAGS_DEFAULT = NamingFlags.ALL_DEFAULT & ~NamingFlags.PREFIX
'''0x1E'''


class LoggingFlags(IntEnum):
    NONE = 0x000
    TRACE = 0x001
    DEBUG = 0x002
    INFO = 0x004
    WARN = 0x008
    ERROR = 0x010
    FATAL = 0x800
    # unused
    ALL = FATAL | ERROR | WARN | INFO | DEBUG | TRACE
    '''0x81F'''

    def __str__(self) -> str:
        return f'{self.name} (0x{self.value:03X})'


LOGGING_FLAGS = {
    'error': f'0x{LoggingFlags.ERROR.value:03X}',
    'warn': f'0x{LoggingFlags.WARN.value:03X}',
    'info': f'0x{LoggingFlags.INFO.value:03X}',
    'debug': f'0x{LoggingFlags.DEBUG.value:03X}',
    'trace': f'0x{LoggingFlags.TRACE.value:03X}',
}
'''{\n\n'error': '0x010',\n\n'warn': '0x008',\n\n'info': '0x004',\n\n'debug': '0x002',\n\n'trace': '0x001'\n\n}'''
LOGGING_FLAGS_DEFAULT = LoggingFlags.INFO
'''0x004'''

ACTION_STORE_TRUE = 'store_true'
ACTION_APPEND = 'append'

SRC_PATH = os.path.abspath(os.path.dirname(__file__)).replace('\\', SLASH)
FILE_LOC_TAGS = f'{SRC_PATH}/../2tags/rv_tags.json'
FILE_LOC_CATS = f'{SRC_PATH}/../3categories/rv_cats.json'
FILE_LOC_ARTS = f'{SRC_PATH}/../4artists/rv_arts.json'
FILE_LOC_PLAS = f'{SRC_PATH}/../5playlists/rv_playlists.json'
FILE_LOC_TAG_ALIASES = f'{SRC_PATH}/../2tags/tag_aliases.json'
FILE_LOC_TAG_CONFLICTS = f'{SRC_PATH}/../2tags/tag_conflicts.json'


class DownloadResult(IntEnum):
    SUCCESS = 0
    FAIL_NOT_FOUND = 1
    FAIL_RETRIES = 2
    FAIL_ALREADY_EXISTS = 3
    FAIL_SKIPPED = 4
    FAIL_DELETED = 5
    FAIL_FILTERED_OUTER = 6
    FAIL_EMPTY_HTML = 7

    RESULT_MASK_ALL = ((1 << SUCCESS) | (1 << FAIL_NOT_FOUND) | (1 << FAIL_RETRIES) | (1 << FAIL_ALREADY_EXISTS) |
                       (1 << FAIL_SKIPPED) | (1 << FAIL_DELETED) | (1 << FAIL_FILTERED_OUTER) | (1 << FAIL_EMPTY_HTML))
    RESULT_MASK_CRITICAL = (RESULT_MASK_ALL & ~((1 << SUCCESS) | (1 << FAIL_SKIPPED) | (1 << FAIL_ALREADY_EXISTS)))

    def __str__(self) -> str:
        return f'{self.name} (0x{self.value:02X})'


class Mem:
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024


class IntPair(NamedTuple):
    first: int
    second: int


class StrPair(NamedTuple):
    first: str
    second: str


class Duration(NamedTuple):
    min: int
    max: int

    def __bool__(self) -> bool:
        return any(bool(getattr(self, _)) for _ in self._fields)


class NumRange(NamedTuple):
    min: float
    max: float

    def __bool__(self) -> bool:
        return any(bool(getattr(self, _)) for _ in self._fields)

#
#
#########################################
