# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from typing import Protocol

from .containers import DownloadParams, FileSystemMapping


class DownloadParamsCallback(Protocol):
    def execute(self, url: str, download_params: DownloadParams) -> None: ...
    def __str__(self) -> str: ...


class FileSystemCallback(Protocol):
    def execute(self, root_id: str, ftree: FileSystemMapping) -> None: ...
    def __str__(self) -> str: ...

#
#
#########################################
