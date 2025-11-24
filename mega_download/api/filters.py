# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from collections.abc import Iterable
from typing import Protocol

from .containers import File
from .defs import Mem, NumRange

__all__ = ('FileSizeFilter', 'Filter', 'any_filter_matching')


class Filter(Protocol):
    def matches(self, file: File) -> bool: ...
    def __str__(self) -> str: ...


class FileSizeFilter:
    """
    Filters files by file size in Megabytes (min .. max)
    """
    resolution = Mem.MB

    def __init__(self, irange: NumRange) -> None:
        self._range = irange

    def matches(self, file: File) -> bool:
        file_size = file['s']
        file_size /= FileSizeFilter.resolution
        return not self._range.min <= file_size <= self._range.max

    def __str__(self) -> str:
        return f'{self.__class__.__name__}<{self._range!s}>'


def any_filter_matching(file: File, filters: Iterable[Filter]) -> Filter | None:
    for ffilter in filters:
        if ffilter.matches(file):
            return ffilter
    return None

#
#
#########################################
