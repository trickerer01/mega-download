# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from typing import Protocol

from .containers import DownloadParams

__all__ = ('DownloadParamsCallback',)


class DownloadParamsCallback(Protocol):
    def execute(self, download_params: DownloadParams) -> None: ...
    def __str__(self) -> str: ...

#
#
#########################################
