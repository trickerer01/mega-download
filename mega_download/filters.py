# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from .api.containers import File
from .api.defs import Mem, NumRange


class FileSizeFilter:
    """
    Filters files by file size in Megabytes (min .. max)
    """
    resolution = Mem.MB

    def __init__(self, irange: NumRange) -> None:
        self._range = irange

    def filters_out(self, file: File) -> bool:
        file_size = file['s']
        file_size /= FileSizeFilter.resolution
        return not self._range.min <= file_size <= self._range.max

    def __str__(self) -> str:
        return f'{self.__class__.__name__}<{self._range!s}>'

#
#
#########################################
