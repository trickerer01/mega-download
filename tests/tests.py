# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import functools
import pathlib
from collections.abc import Callable
from tempfile import TemporaryDirectory
from unittest import TestCase

from mega_download import APP_NAME, main_sync
from mega_download.api import DownloadMode, RequestQueue
from mega_download.config import Config
from mega_download.defs import LoggingFlags
from mega_download.logger import Log
from mega_download.util import compose_link_v2

RUN_CONN_TESTS = 0


def test_prepare(log=False) -> Callable[[], Callable[[], None]]:
    def invoke1(test_func: Callable[[...], None]) -> Callable[[], None]:
        @functools.wraps(test_func)
        def invoke_test(*args, **kwargs) -> None:
            def set_up_test() -> None:
                Log._disabled = not log
                Config._reset()
                RequestQueue._reset()
            set_up_test()
            test_func(*args, **kwargs)
        return invoke_test
    return invoke1


class CmdTests(TestCase):
    @test_prepare()
    def test_config_integrity(self):
        assert all(hasattr(Config, _) for _ in Config.NAMESPACE_VARS_REMAP.values())
        print(f'{self._testMethodName} passed')


class DownloadTests(TestCase):
    @test_prepare()
    def test_download_touch_1(self):
        if not RUN_CONN_TESTS:
            return
        with TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_') as tempdir_name:
            tempfile_name = 'oem_mx/c_p_mx.edf'
            tempfile_path = pathlib.Path(tempdir_name) / tempfile_name
            templink = compose_link_v2('6cE1AazL', 'jAsE1BiZ', '9ISiN871PS8mBAKIkiSLdw')
            tempfile_size = 0
            arglist = [
                templink,
                '--path', tempfile_path.parent.parent.as_posix(),
                '--download-mode', DownloadMode.TOUCH.value,
                '--log-level', LoggingFlags.INFO.name.lower(),
            ]
            main_sync(arglist)
            self.assertTrue(tempfile_path.exists())
            self.assertEqual(tempfile_size, tempfile_path.stat().st_size)
        print(f'{self._testMethodName} passed')

    @test_prepare()
    def test_download_touch_2(self):
        if not RUN_CONN_TESTS:
            return
        with TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_') as tempdir_name:
            tempfile_name = 'KTM_CBF_18.pnt'
            tempfile_path = pathlib.Path(tempdir_name) / tempfile_name
            templink = compose_link_v2('', 'WVczzLpB', 'faIpcuNadIMU4uLyNQ1LfWFhAHBwPewtxxSiTIdeHWI')
            tempfile_size = 0
            arglist = [
                templink,
                '--path', tempfile_path.parent.as_posix(),
                '--download-mode', DownloadMode.TOUCH.value,
                '--log-level', LoggingFlags.INFO.name.lower(),
            ]
            main_sync(arglist)
            self.assertTrue(tempfile_path.exists())
            self.assertEqual(tempfile_size, tempfile_path.stat().st_size)
        print(f'{self._testMethodName} passed')

    @test_prepare()
    def test_download_full_1(self):
        if not RUN_CONN_TESTS:
            return
        with TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_') as tempdir_name:
            tempfile_name = 'oem_mx/p_mx_s.edf'
            tempfile_path = pathlib.Path(tempdir_name) / tempfile_name
            templink = compose_link_v2('6cE1AazL', 'qZsWyJ5K', '9ISiN871PS8mBAKIkiSLdw')
            tempfile_size = 1172614
            arglist = [
                templink,
                '--path', tempfile_path.parent.parent.as_posix(),
                '--download-mode', DownloadMode.FULL.value,
                '--log-level', LoggingFlags.INFO.name.lower(),
            ]
            main_sync(arglist)
            self.assertTrue(tempfile_path.exists())
            self.assertEqual(tempfile_size, tempfile_path.stat().st_size)
        print(f'{self._testMethodName} passed')

    @test_prepare()
    def test_download_full_2(self):
        if not RUN_CONN_TESTS:
            return
        with TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_') as tempdir_name:
            tempfile_name = 'KTM_CBF_PUB.pnt'
            tempfile_path = pathlib.Path(tempdir_name) / tempfile_name
            templink = compose_link_v2('', 'PZFCVYYK', 'El6KmJzu_Z763NzYrLlCUdD_v2W1thlw22B-w3ko7u8')
            tempfile_size = 5040037
            arglist = [
                templink,
                '--path', tempfile_path.parent.as_posix(),
                '--download-mode', DownloadMode.FULL.value,
                '--log-level', LoggingFlags.INFO.name.lower(),
            ]
            main_sync(arglist)
            self.assertTrue(tempfile_path.exists())
            self.assertEqual(tempfile_size, tempfile_path.stat().st_size)
        print(f'{self._testMethodName} passed')

#
#
#########################################
