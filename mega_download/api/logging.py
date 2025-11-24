# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from typing import Protocol

__all__ = ('Log', 'Logger', 'set_logger')


class Logger(Protocol):
    @staticmethod
    def log(text: str) -> None: ...
    @staticmethod
    def fatal(text: str) -> None: ...
    @staticmethod
    def error(text: str) -> None: ...
    @staticmethod
    def warn(text: str) -> None: ...
    @staticmethod
    def info(text: str) -> None: ...
    @staticmethod
    def debug(text: str) -> None: ...
    @staticmethod
    def trace(text: str) -> None: ...


class LoggerWrapper:
    logger = Logger

    @staticmethod
    def fatal(text: str) -> None:
        LoggerWrapper.logger.fatal(text)

    @staticmethod
    def error(text: str) -> None:
        LoggerWrapper.logger.error(text)

    @staticmethod
    def warn(text: str) -> None:
        LoggerWrapper.logger.warn(text)

    @staticmethod
    def info(text: str) -> None:
        LoggerWrapper.logger.info(text)

    @staticmethod
    def debug(text: str) -> None:
        LoggerWrapper.logger.debug(text)

    @staticmethod
    def trace(text: str) -> None:
        LoggerWrapper.logger.trace(text)


def set_logger(logger: Logger) -> None:
    LoggerWrapper.logger = logger


Log = LoggerWrapper

#
#
#########################################
