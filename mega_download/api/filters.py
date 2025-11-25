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

__all__ = ('Filter', 'any_filter_matching')


class Filter(Protocol):
    def matches(self, file: File) -> bool: ...
    def __str__(self) -> str: ...


def any_filter_matching(file: File, filters: Iterable[Filter]) -> Filter | None:
    for ffilter in filters:
        if ffilter.matches(file):
            return ffilter
    return None

#
#
#########################################
