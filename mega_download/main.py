# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import sys
from asyncio import get_running_loop, run, sleep
from collections.abc import Sequence

from .api import DownloadMode, Mega, MegaNZError, MegaOptions
from .cmdargs import HelpPrintExitException, prepare_arglist
from .config import Config
from .defs import MIN_PYTHON_VERSION, MIN_PYTHON_VERSION_STR
from .filters import FileSizeFilter
from .logger import Log
from .version import APP_NAME, APP_VERSION

__all__ = ('main_async', 'main_sync')


def at_startup() -> None:
    """Inits logger. Reports python version and run options"""
    argv_set = set(sys.argv)
    if argv_set.intersection({'--disable-log-colors', '-g'}):
        Config.nocolors = True
    Log.init()
    if argv_set.intersection({'--version', '--help'}):
        return
    Log.debug(f'Python {sys.version}\n{APP_NAME} ver {APP_VERSION}\nCommand-line args: {" ".join(sys.argv)}')


def make_mega_options() -> MegaOptions:
    options = MegaOptions(
        dest_base=Config.dest_base,
        retries=Config.retries,
        timeout=Config.timeout,
        proxy=Config.proxy,
        extra_headers=Config.extra_headers,
        extra_cookies=Config.extra_cookies,
        filters=(FileSizeFilter(Config.filter_filesize),),
        download_mode=DownloadMode(Config.download_mode),
        logger=Log,
    )
    return options


async def main(args: Sequence[str]) -> int:
    try:
        prepare_arglist(args)
    except HelpPrintExitException:
        return 0

    try:
        async with Mega(make_mega_options()) as mega:
            results = [await mega.download_url(link) for link in Config.links]
            Log.info(f'{results!s}' or 'Nothing')
        return 0
    except MegaNZError:
        import traceback
        Log.fatal(f'Catched MegaNZError!\n{traceback.format_exc()}')
        return -2
    except Exception as e:
        import traceback
        Log.fatal(f'Unhandled exception {e.__class__.__name__}!\n{traceback.format_exc()}')
        return -3


async def run_main(args: Sequence[str]) -> int:
    res = await main(args)
    await sleep(0.5)
    return res


async def main_async(args: Sequence[str]) -> int:
    assert sys.version_info >= MIN_PYTHON_VERSION, f'Minimum python version required is {MIN_PYTHON_VERSION_STR}!'
    try:
        return await run_main(args)
    except (KeyboardInterrupt, SystemExit):
        Log.warn('Warning: catched KeyboardInterrupt/SystemExit...')
        return -1


def main_sync(args: Sequence[str]) -> int:
    at_startup()
    try:
        loop = get_running_loop()
    except RuntimeError:  # no current event loop
        loop = None
    run_func = loop.run_until_complete if loop else run
    return run_func(main_async(args))


if __name__ == '__main__':
    exit(main_sync(sys.argv[1:]))

#
#
#########################################
