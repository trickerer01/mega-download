# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from __future__ import annotations

import datetime
import pathlib
from enum import IntEnum
from typing import NamedTuple, TypeAlias, TypedDict

IntVector: TypeAlias = tuple[int, ...]
'''Tuple of ints of length 0, 2, 4 or 6'''


class Attributes(TypedDict):
    n: str  # Name


class UserInfo(TypedDict):
    tsid: str  # Session id
    csid: str  # Session id
    k: str  # User key
    u: str  # User Id
    ach: int  # always 1


class NodeType(IntEnum):
    DUMMY = -1
    FILE = 0
    FOLDER = 1
    ROOT_FOLDER = 2
    INBOX = 3
    TRASH = 4


class Node(TypedDict):
    t: NodeType
    h: str  # Id
    p: str  # Parent Id
    a: str  # Encrypted attributes (within this: 'n' Name)
    k: str  # Node key
    u: str  # User Id
    ts: int  # Timestamp
    g: str  # Access URL
    # k: str  # Public access key (parent folder + file)

    #  Non standard properties
    attributes: Attributes  # Decrypted attributes
    k_decrypted: IntVector
    key_decrypted: IntVector  # Decrypted access key (for folders, its values if the same as 'k_decrypted')

    timestamp: datetime.datetime


class File(Node):
    su: str  # Shared user Id, only present present in shared files / folder
    sk: str  # Shared key, only present present in shared files / folder

    fh: str  # Root id? (pure file link)

    at: str  # File specific attributes (encrypted)
    s: int  # Size

    #  Non standard properties
    iv: IntVector
    meta_mac: IntVector
    sk_decrypted: IntVector

    num_in_queue: int


class Folder(Node):
    su: str  # Shared user Id, only present present in shared files / folder
    sk: str  # Shared key, only present present in shared files / folder

    f: list[File | Folder]  # User folder children (files or folders)
    ok: list[File | Folder]  # Shared folder children (files or folders)
    s: list[File | Folder]  # List of sub nodes

    #  Non standard properties
    iv: IntVector
    meta_mac: IntVector
    sk_decrypted: IntVector


SharedKey: TypeAlias = dict[str, IntVector]
'''Mapping: (recipient) User Id ('u') -> decrypted value of shared key ('sk')'''
SharedkeysDict: TypeAlias = dict[str, SharedKey]
'''Mapping: (owner) Shared User Id ('su') -> SharedKey'''
FilesMapping: TypeAlias = dict[str, File | Folder]
'''Mapping: parent_id ('p') -> File | Folder'''
FileSystemMapping: TypeAlias = dict[pathlib.PurePosixPath, File | Folder]
'''Mapping: path -> File | Folder'''
FilePathMapping: TypeAlias = dict[pathlib.PurePosixPath, File]
'''Mapping: path -> File'''


class ParsedUrl(NamedTuple):
    folder_id: str
    file_id: str
    key_b64: str

    @staticmethod
    def default() -> ParsedUrl:
        return ParsedUrl('', '', '')


class DownloadParams(NamedTuple):
    index: int
    original_pos: int
    direct_file_url: str
    output_path: pathlib.Path
    file_size: int
    iv: IntVector
    meta_mac: IntVector
    k_decrypted: IntVector


DownloadParamsDump: TypeAlias = dict[str, list[DownloadParams] | str]
FileSystemDump: TypeAlias = FileSystemMapping

#
#
#########################################
