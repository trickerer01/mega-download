# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from enum import IntEnum
from typing import NamedTuple

MIN_PYTHON_VERSION = (3, 10)
MIN_PYTHON_VERSION_STR = f'{MIN_PYTHON_VERSION[0]:d}.{MIN_PYTHON_VERSION[1]:d}'

CONNECT_RETRIES_BASE = 50
CONNECT_TIMEOUT_BASE = 10
CONNECT_TIMEOUT_SOCKET_READ = 30

SLASH = '/'
UTF8 = 'utf-8'


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

HELP_ARG_VERSION = 'Show program\'s version number and exit'
HELP_ARG_PATH = 'Download destination. Default is current folder'
HELP_ARG_PROXY = 'Proxy to use, supports basic authentication'
HELP_ARG_DMMODE = '[Debug] Download (file creation) mode'
HELP_ARG_LINKS = 'Full url to mega.nz shared file or folder'
HELP_ARG_LOGGING = (
    f'Logging level: {{{str(list(LOGGING_FLAGS.keys())).replace(" ", "")[1:-1]}}}.'
    f' All messages equal or above this level will be logged. Default is \'info\''
)
HELP_ARG_NOCOLORS = 'Disable logging level dependent colors in log'
HELP_ARG_HEADER = 'Append additional header. Can be used multiple times'
HELP_ARG_COOKIE = 'Append additional cookie. Can be used multiple times'
HELP_ARG_TIMEOUT = f'Connection timeout (in seconds). Default is \'{CONNECT_TIMEOUT_BASE:d}\''
HELP_ARG_RETRIES = f'Connection retries count. Default is \'{CONNECT_RETRIES_BASE:d}\''
# New
HELP_ARG_FILTERS = 'Available filters: file size (MB), file name (pattern)'
HELP_ARG_DUMP_LINKS = 'Store all gathered links and other misc info for future processing'


class NumRange(NamedTuple):
    min: float
    max: float

    def __bool__(self) -> bool:
        return any(bool(getattr(self, _)) for _ in self._fields)

#
#
#########################################
