# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from defs import (
    CONNECT_RETRIES_BASE,
    DOWNLOAD_MODE_DEFAULT,
    LOGGING_FLAGS,
    # MAX_DEST_SCAN_SUB_DEPTH_DEFAULT,
    # MAX_DEST_SCAN_UPLEVELS_DEFAULT,
    # NAMING_FLAGS_DEFAULT,
)

if False is True:  # for hinting only
    from aiohttp import ClientTimeout  # noqa: I001
    from defs import NumRange

__all__ = ('Config',)


class BaseConfig:
    """Parameters container for params used in both **pages** and **ids** modules"""
    NAMESPACE_VARS_REMAP = {
        'path': 'dest_base',
        # 'fsdepth': 'folder_scan_depth',
        # 'fslevelup': 'folder_scan_levelup',
        # 'naming': 'naming_flags',
        'log_level': 'logging_flags',
        'disable_log_colors': 'nocolors',
        'header': 'extra_headers',
        'cookie': 'extra_cookies',
    }

    def __init__(self) -> None:
        # new
        self.filter_filesize: NumRange | None = None

        # states
        self.aborted: bool = False
        # common
        self.links: list[str] | None = None
        self.dest_base: str | None = None
        self.proxy: str | None = None
        # self.download_without_proxy: bool | None = None
        # self.html_without_proxy: bool | None = None
        # self.folder_scan_depth: int = 0
        # self.folder_scan_levelup: int = 0
        self.download_mode: str | None = None
        # self.continue_mode: bool | None = None
        # self.keep_unfinished: bool | None = None
        # self.no_rename_move: bool | None = None
        # self.naming_flags: int = 0
        self.logging_flags: int = 0
        self.nocolors: bool | None = None
        self.timeout: ClientTimeout | None = None
        self.retries: int = 0
        # self.store_continue_cmdfile: bool | None = None
        # self.report_duplicates: bool | None = None
        self.extra_headers: list[tuple[str, str]] | None = None
        self.extra_cookies: list[tuple[str, str]] | None = None
        # extras (can't be set through cmdline arguments)
        self.nodelay: bool = False

    def make_continue_arguments(self) -> list[str | int | None]:
        arglist = [
            '-path', self.dest_base, '-continue', '--store-continue-cmdfile',
            '-log', next(x for x in LOGGING_FLAGS if int(LOGGING_FLAGS[x], 16) == self.logging_flags),
            # *(('-naming', self.naming_flags) if self.naming_flags != NAMING_FLAGS_DEFAULT else ()),
            *(('-dmode', self.download_mode) if self.download_mode != DOWNLOAD_MODE_DEFAULT else ()),
            # *(('-fsdepth', self.folder_scan_depth) if self.folder_scan_depth != MAX_DEST_SCAN_SUB_DEPTH_DEFAULT else ()),
            # *(('-fslevel', self.folder_scan_levelup) if self.folder_scan_levelup != MAX_DEST_SCAN_UPLEVELS_DEFAULT else ()),
            *(('-proxy', self.proxy) if self.proxy else ()),
            # *(('--download-without-proxy',) if self.download_without_proxy else ()),
            # *(('--html-without-proxy',) if self.html_without_proxy else ()),
            *(('-timeout', int(self.timeout.connect)) if self.timeout and self.timeout.connect else ()),
            *(('-retries', self.retries) if self.retries != CONNECT_RETRIES_BASE else ()),
            # *(('-unfinish',) if self.keep_unfinished else ()),
            # *(('-nomove',) if self.no_rename_move else ()),
        ]
        return arglist

    def _reset(self) -> None:
        self.__init__()  # noqa: PLC2801

    def on_scan_abort(self) -> None:
        self.aborted = True

    @property
    def dm(self) -> str | None:
        return self.download_mode


Config: BaseConfig = BaseConfig()

#
#
#########################################
