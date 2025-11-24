# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import os
from argparse import ZERO_OR_MORE, ArgumentParser, Namespace
from collections.abc import Sequence

from .api.defs import DOWNLOAD_MODE_DEFAULT, DOWNLOAD_MODES
from .config import Config
from .defs import (
    ACTION_APPEND,
    ACTION_STORE_TRUE,
    CONNECT_RETRIES_BASE,
    HELP_ARG_COOKIE,
    HELP_ARG_DMMODE,
    HELP_ARG_FILTERS,
    HELP_ARG_HEADER,
    HELP_ARG_LINKS,
    HELP_ARG_LOGGING,
    HELP_ARG_NOCOLORS,
    HELP_ARG_PATH,
    HELP_ARG_PROXY,
    HELP_ARG_RETRIES,
    HELP_ARG_TIMEOUT,
    HELP_ARG_VERSION,
    LOGGING_FLAGS_DEFAULT,
    UTF8,
)
from .logger import Log
from .validators import (
    log_level,
    positive_int,
    valid_kwarg,
    valid_path,
    valid_proxy,
    valid_range,
    valid_timeout,
)
from .version import APP_NAME, APP_VERSION

__all__ = ('HelpPrintExitException', 'prepare_arglist')

DM_DEFAULT = DOWNLOAD_MODE_DEFAULT
"""'full'"""
LOGGING_DEFAULT = LOGGING_FLAGS_DEFAULT
'''0x004'''

PARSER_ARG_TITLE = 'zzzparser_type'
PARSER_TITLE_FILE = 'file'
PARSER_TITLE_CMD = 'cmd'
EXISTING_PARSERS = {PARSER_TITLE_CMD, PARSER_TITLE_FILE}
"""'file','cmd'"""

PARSED_ARGS_NO_CONSUME = {
    PARSER_ARG_TITLE,
}


class HelpPrintExitException(Exception):
    pass


def read_cmdfile(cmdfile_path: str) -> list[str]:
    """Read cmd args from a text file"""
    with open(cmdfile_path, 'rt', encoding=UTF8) as cmdfile:
        return [_.strip(' \n\ufeff') for _ in cmdfile]


def is_parsed_file(parsed_result: Namespace) -> bool:
    return getattr(parsed_result, PARSER_ARG_TITLE) == PARSER_TITLE_FILE


def is_parsed_cmdfile(parsed_result: Namespace) -> bool:
    return is_parsed_file(parsed_result)


def validate_parsed(parser: ArgumentParser, args: Sequence[str], default_sub: ArgumentParser) -> Namespace:
    errors_to_print: list[str] = []
    parsed, unks = parser.parse_known_args(args) if args[0] in EXISTING_PARSERS else default_sub.parse_known_args(args)
    if not is_parsed_cmdfile(parsed):
        taglist: Sequence[str]
        for i, taglist in enumerate((parsed.links, unks)):
            for tag in taglist:
                try:
                    valid_tag = tag
                    if i > 0:
                        parsed.links.append(valid_tag)
                except (AssertionError, ValueError):
                    errors_to_print.append(f'Invalid extra tag: \'{tag}\'')
        if errors_to_print:
            Log.fatal('\n'.join(errors_to_print))
            raise ValueError
    return parsed


def execute_parser(parser: ArgumentParser, default_sub: ArgumentParser, args: Sequence[str]) -> Namespace:
    try:
        assert args
        parsed = validate_parsed(parser, args, default_sub)
        while is_parsed_cmdfile(parsed):
            parsed = prepare_arglist_type(read_cmdfile(parsed.path))
        return parsed
    except SystemExit:
        raise HelpPrintExitException
    except Exception:
        from traceback import format_exc
        default_sub.print_help()
        Log.fatal(format_exc())
        raise HelpPrintExitException


def create_parsers() -> tuple[ArgumentParser, ArgumentParser, ArgumentParser]:
    parser = ArgumentParser(add_help=False)
    subs = parser.add_subparsers()
    par_file = subs.add_parser(PARSER_TITLE_FILE, description='Run using text file containing cmdline arguments', add_help=False)
    par_cmd = subs.add_parser(PARSER_TITLE_CMD, description='', add_help=False)
    [p.add_argument('--help', action='help', help='Print this message') for p in (par_file, par_cmd)]
    [p.add_argument('--version', action='version', help=HELP_ARG_VERSION, version=f'{APP_NAME} {APP_VERSION}') for p in (par_file, par_cmd)]
    [p.set_defaults(**{PARSER_ARG_TITLE: t}) for p, t in zip((par_file, par_cmd), (PARSER_TITLE_FILE, PARSER_TITLE_CMD), strict=True)]
    return parser, par_file, par_cmd


def parse_arglist(args: Sequence[str]) -> Namespace:
    parser, _, par_cmd = create_parsers()
    par_cmd.usage = (
        '\n       main.py [options...] URL [URL ...]'
    )

    par_cmd.add_argument('-o', '--path', default=valid_path(os.path.abspath(os.path.curdir)), help=HELP_ARG_PATH, type=valid_path)
    par_cmd.add_argument('-x', '--proxy', metavar='#type://[u:p@]a.d.d.r:port', default=None, help=HELP_ARG_PROXY, type=valid_proxy)
    par_cmd.add_argument('-t', '--timeout', metavar='#seconds', default=valid_timeout(''), help=HELP_ARG_TIMEOUT, type=valid_timeout)
    par_cmd.add_argument('-r', '--retries', metavar='#number', default=CONNECT_RETRIES_BASE, help=HELP_ARG_RETRIES, type=positive_int)
    par_cmd.add_argument('-v', '--log-level', default=LOGGING_DEFAULT, help=HELP_ARG_LOGGING, type=log_level)
    par_cmd.add_argument('-g', '--disable-log-colors', action=ACTION_STORE_TRUE, help=HELP_ARG_NOCOLORS)
    par_cmd.add_argument('-h', '--header', metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_HEADER, type=valid_kwarg)
    par_cmd.add_argument('-c', '--cookie', metavar='#name=value', action=ACTION_APPEND, help=HELP_ARG_COOKIE, type=valid_kwarg)
    par_cmd.add_argument('-fs', '--filter-filesize', metavar='#min-max', default=valid_range(''), help=HELP_ARG_FILTERS, type=valid_range)
    par_cmd.add_argument('-d', '--download-mode', default=DM_DEFAULT, help=HELP_ARG_DMMODE, choices=DOWNLOAD_MODES)
    par_cmd.add_argument(dest='links', nargs=ZERO_OR_MORE, help=HELP_ARG_LINKS)

    return execute_parser(parser, par_cmd, args)


def prepare_arglist_type(args: Sequence[str]) -> Namespace:
    parsed = parse_arglist(args)
    return parsed


def prepare_arglist(args: Sequence[str]) -> None:
    parsed = prepare_arglist_type(args)
    for pp in vars(parsed):
        param = Config.NAMESPACE_VARS_REMAP.get(pp, pp)
        if param in vars(Config):
            setattr(Config, param, getattr(parsed, pp, getattr(Config, param)))
        elif param not in PARSED_ARGS_NO_CONSUME:
            Log.error(f'Argument list param {param} was not consumed!')

#
#
#########################################
