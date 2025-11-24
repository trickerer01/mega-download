# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import datetime
import os
from enum import IntEnum
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

# download (file creation) mode
DOWNLOAD_MODE_FULL = 'full'
DOWNLOAD_MODE_TOUCH = 'touch'
DOWNLOAD_MODE_SKIP = 'skip'
DOWNLOAD_MODES = (DOWNLOAD_MODE_FULL, DOWNLOAD_MODE_TOUCH, DOWNLOAD_MODE_SKIP)
'''('full','touch','skip')'''
DOWNLOAD_MODE_DEFAULT = DOWNLOAD_MODE_FULL
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


HELP_ARG_FILTERS = 'Available filters: file size (in Megabytes)'


HELP_ARG_VERSION = 'Show program\'s version number and exit'
HELP_ARG_GET_MAXID = 'Print maximum id and exit'
HELP_ARG_ID_END = 'End video id'
HELP_ARG_ID_COUNT = 'Ids count to process'
HELP_ARG_ID_START = 'Start video id. Required'
HELP_ARG_PAGE_END = 'End page number'
HELP_ARG_PAGE_COUNT = 'Pages count to process'
HELP_ARG_PAGE_START = 'Start page number. Default is \'1\''
HELP_ARG_BEGIN_STOP_ID = 'Video id lower / upper bounds filter to only download videos where \'begin_id >= video_id >= stop_id\''
HELP_ARG_PREDICT_ID_GAPS = (
    'Enable ids known to be non-existent prediction. When video is uploaded to the website post id usually gets incremented more than once.'
    ' This options allows to skip gaps within id ranges known to contain them, this may cut scan time by up to -75%%.\n'
    ' Automatically disables itself if encounters a contradicting post validity sequence.'
    ' WARNING: unsafe - may skip valid posts (not trying to request post info), use at your own risk'
)
HELP_ARG_IDSEQUENCE = (
    'Use video id sequence instead of id range. This disables start / count / end id parametes and expects an id sequence among extra tags.'
    ' Sequence structure: (id=<id1>~id=<id2>~id=<id3>~...~id=<idN>)'
)
HELP_ARG_LINKSEQUENCE = (
    'Use links instead of id range. This disables start / count / end id parametes and expects at least one link among extra tags'
)
HELP_ARG_PATH = 'Download destination. Default is current folder'
HELP_ARG_FSDEPTH = (
    f'Number of subfolder levels to walk from base destination folder scanning for existing downloads.'
    f' Default is \'{MAX_DEST_SCAN_SUB_DEPTH_DEFAULT:d}\''
)
HELP_ARG_FSLEVELUP = (
    'Folder levels to go up before scanning for existing files, increases scan depth. Destination folder is always checked'
)
HELP_ARG_SESSION_ID = (
    '\'PHPSESSID\' cookie. Some tags are hidden and cannot be searched for without logging in.'
    ' Using this cookie from logged in account resolves that problem (tag/artist/category blacklists still apply)'
)
HELP_ARG_QUALITY = f'Video quality. Default is \'{DEFAULT_QUALITY}\'. If not found, best quality found is used (up to 4K)'
HELP_ARG_PROXY = 'Proxy to use, supports basic authentication'
HELP_ARG_PROXYNODOWN = 'Don\'t use proxy to connect to file servers if they differ from the main host'
HELP_ARG_PROXYNOHTML = 'Don\'t use proxy to connect to the main host'
HELP_ARG_DMMODE = '[Debug] Download (file creation) mode'
HELP_ARG_ALL_PAGES = 'Do not interrupt pages scan if encountered a page having all post ids filtered out'
HELP_ARG_LINKS = 'Full url to mega.nz shared file or folder'
HELP_ARG_DWN_SCENARIO = (
    'Download scenario. This allows to scan for tags and sort videos accordingly in a single pass.'
    ' Useful when you have several queries you need to process for same id range.'
    ' Format:'
    ' "{SUBDIR1}: tag1 tag2; {SUBDIR2}: tag3 tag4".'
    ' You can also use following arguments in each subquery: -quality, -duration, -minscore, -minrating, -utp, -seq.'
    ' Example:'
    ' \'python ids.py -path ... -start ... -end ... --download-scenario'
    ' "1g: 1girl -quality 480p; 2g: 2girls -quality 720p -minscore 150 -utp always"\''
)
HELP_ARG_STORE_CONTINUE_CMDFILE = (
    'Store and automatically update cmd file which allows to later continue with unfinished download queue'
    ' (using ids module, file mode, check README for more info)'
)
HELP_ARG_SOLVE_TAG_CONFLICTS = (
    'Detect and remove simple tags that are contradictory to one or more other - more descriptive - tags (if no similar tags were found).'
    ' Mainly to prevent posts being accidently filtered out by extra \'tags\' / \'-tags\'.'
    ' Example: a post tagged with \'solo\' tag, \'1boy1girl\' or \'2girls\' and neither \'solo_male\' nor \'solo_female\''
    ' will have its \'solo\' tag removed as it is less descriptive and probably a mistake'
)
HELP_ARG_REPORT_DUPLICATES = (
    f'Report duplicate downloaded posts (regardless of quality) after initial destination folder scan.'
    f' Simplified - only names starting with \'{PREFIX}\''
)
HELP_ARG_CHECK_UPLOADER = (
    'Apply extra \'tag\' / \'-tag\' filters to uploader name.'
    ' By default only tags, categories and artists are checked by extra tags'
    ' and uploader can only be checked using its own syntax: positive \'u:{name}\' or negative \'-u:{name}\''
)
HELP_ARG_CHECK_TITLEDESC = (
    'Apply extra \'tag\' / \'-tag\' filters to title / description.'
    ' All exta \'tag\'s will be converted to wildcard tags and will have underscores replaced with spaces during this match.'
    ' Post is considered matching extra tags if either its tags or its title / description matches all extra \'tag\'s (positive filtering)'
    ' and neither its tags nor its title / description matches extra \'-tags\' (negative filtering)'
)
HELP_ARG_MINRATING = (
    'Rating percentage filter, 0-100.'
    ' Videos having rating below this value will be skipped, unless rating extraction fails - in that case video always gets a pass'
)
HELP_ARG_MINSCORE = (
    'Score filter (likes minus dislikes).'
    ' Videos having score below this value will be skipped, unless score extraction fails - in that case video always gets a pass'
)
HELP_ARG_CMDFILE = (
    'Full path to file containing cmdline arguments. Useful when cmdline length exceeds maximum for your OS.'
    ' Windows: ~32000, MinGW: ~4000 to ~32000, Linux: ~127000+. Check README for more info'
)
HELP_ARG_NAMING = (
    f'File naming flags: {str(NAMING_FLAGS).replace(" ", "").replace(":", "=")}.'
    f' You can combine them via names \'prefix|score|title\', otherwise it has to be an int or a hex number.'
    f' Default is \'full\''
)
HELP_ARG_LOGGING = (
    f'Logging level: {{{str(list(LOGGING_FLAGS.keys())).replace(" ", "")[1:-1]}}}.'
    f' All messages equal or above this level will be logged. Default is \'info\''
)
HELP_ARG_NOCOLORS = 'Disable logging level dependent colors in log'
HELP_ARG_HEADER = 'Append additional header. Example: \'-header user_agent=googlebot/1.1\'. Can be used multiple times'
HELP_ARG_COOKIE = 'Append additional cookie. Example: \'-cookie shm_user=user1\'. Can be used multiple times'
HELP_ARG_DUMP_SCREENSHOTS = 'Save timeline screenshots (webp, very slow, ignores download mode)'
HELP_ARG_DUMP_INFO = 'Save tags / descriptions / comments to text file (separately)'
HELP_ARG_SKIP_EMPTY_LISTS = 'Do not store tags / descriptions / comments list if it contains no useful data'
HELP_ARG_MERGE_LISTS = 'Merge exising tags / descriptions / comments list(s) with saved info (only if saving is enabled)'
HELP_ARG_CONTINUE = 'Try to continue unfinished files, may be slower if most files already exist'
HELP_ARG_UNFINISH = 'Do not clean up unfinished files on interrupt'
HELP_ARG_NOMOVE = 'In continue mode instead of moving already existing file to destination folder download to its original location'
HELP_ARG_TIMEOUT = f'Connection timeout (in seconds). Default is \'{CONNECT_TIMEOUT_BASE:d}\''
HELP_ARG_RETRIES = f'Connection retries count. Default is \'{CONNECT_RETRIES_BASE:d}\''
HELP_ARG_THROTTLE = 'Download speed threshold (in KB/s) to assume throttling, drop connection and retry'
HELP_ARG_THROTTLE_AUTO = 'Enable automatic throttle threshold adjustment when crossed too many times in a row'
HELP_ARG_FAVORITES = 'User id (integer, filters still apply)'
HELP_ARG_UPLOADER = 'Uploader user id (integer, filters still apply)'
HELP_ARG_MODEL = 'Artist name (scan artist\'s page(s) instead of using search, filters still apply)'


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
