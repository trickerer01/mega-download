# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import base64
import hashlib
import json
import random
import struct
from collections.abc import Sequence

from Crypto.Cipher import AES

from api.containers import Attributes
from api.defs import EMPTY_IV, LATIN1, UINT32_MAX, UTF8

__all__ = (
    'base64_to_ints',
    'base64_url_decode',
    'base64_url_encode',
    'decrypt_attr',
    'decrypt_key',
    'encrypt_key',
    'ints_to_base64',
    'make_hashcash_token',
    'pack_sequence',
    'pad_bytes_end',
    'unpack_sequence',
    'urand',
)


def urand() -> int:
    return random.randint(0, UINT32_MAX)


def pad_bytes_end(data: bytes | memoryview, *, amount: int) -> bytes:
    data_bytes = data if isinstance(data, bytes) else data.tobytes()
    if len(data_bytes) % amount:
        padding = b'\0' * (amount - len(data_bytes) % amount)
        return data_bytes + padding
    return data_bytes


def pack_sequence(array: Sequence[int]) -> bytes:
    return struct.pack(f'>{len(array):d}I', *array)


def unpack_sequence(data: bytes) -> tuple[int, ...]:
    assert isinstance(data, bytes)  # required
    data_padded = pad_bytes_end(data, amount=4)  # sizeof(uint32)
    return struct.unpack(f'>{(len(data_padded) >> 2):d}I', data_padded)


def _encrypt_eas_cbc(data: bytes, key: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, EMPTY_IV).encrypt(data)


def _decrypt_aes_cbc(data: bytes, key: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, EMPTY_IV).decrypt(data)


def _encrypt_aes_cbc_arr(ints: Sequence[int], key: Sequence[int]) -> tuple[int, ...]:
    return unpack_sequence(_encrypt_eas_cbc(pack_sequence(ints), pack_sequence(key)))


def _decrypt_aes_cbc_ints(ints: Sequence[int], key: Sequence[int]) -> tuple[int, ...]:
    return unpack_sequence(_decrypt_aes_cbc(pack_sequence(ints), pack_sequence(key)))


def encrypt_key(ints: Sequence[int], key: Sequence[int]) -> tuple[int, ...]:
    return sum((_encrypt_aes_cbc_arr(ints[index:index + 4], key) for index in range(0, len(ints), 4)), ())


def decrypt_key(ints: Sequence[int], key: Sequence[int]) -> tuple[int, ...]:
    return sum((_decrypt_aes_cbc_ints(ints[index:index + 4], key) for index in range(0, len(ints), 4)), ())


def decrypt_attr(attr: bytes, key: Sequence[int]) -> Attributes:
    attr_bytes = _decrypt_aes_cbc(attr, pack_sequence(key))
    try:
        attr_str = attr_bytes.decode(UTF8).rstrip('\0')
    except UnicodeDecodeError:
        attr_str = attr_bytes.decode(LATIN1).rstrip('\0')
    if attr_str.startswith('MEGA{"'):
        start = 4
        end = attr_str.find('}', start + 1) + 1
        if end > start:
            ret_data: dict[str, str] = json.loads(attr_str[start:end])
            return ret_data
        else:
            raise ValueError(f'Failed to decode attr, raw was: \'{attr_str}\'')
    else:
        return Attributes(n='Unknown')


def base64_to_ints(string: str) -> tuple[int, ...]:
    return unpack_sequence(base64_url_decode(string))


def base64_url_decode(data: str) -> bytes:
    data += '=='[(2 - len(data) * 3) % 4:]
    for search, replace in (('-', '+'), ('_', '/'), (',', '')):
        data = data.replace(search, replace)
    return base64.b64decode(data)


def base64_url_encode(data: bytes) -> str:
    data_bytes = base64.b64encode(data)
    data_str = data_bytes.decode()
    for search, replace in (('+', '-'), ('/', '_'), ('=', '')):
        data_str = data_str.replace(search, replace)
    return data_str


def ints_to_base64(array: Sequence[int]) -> str:
    return base64_url_encode(pack_sequence(array))


def _b64decode_urlsafe(data_str: str) -> bytes:
    return base64.urlsafe_b64decode(data_str + '=' * (-len(data_str) % 4))


def _b64encode_urlsafe(data_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(data_bytes).decode(UTF8).rstrip('=')


def make_hashcash_token(challenge: str) -> str:
    # https://github.com/gpailler/MegaApiClient/issues/248#issuecomment-2692361193
    parts = challenge.split(':', 3)
    version_str, easiness_str, _, token_str = tuple(parts)
    if not version_str.isnumeric() or int(version_str) != 1:
        raise ValueError(f'Hashcash challenge version is {version_str} != 1')

    assert easiness_str.isnumeric(), f'Hashcash easiness is not numeric (\'{easiness_str}\')!'
    easiness = int(easiness_str)
    base = ((easiness & ((1 << 6) - 1)) << 1) + 1  # base = ((easiness & 63) << 1) + 1
    shifts = (easiness >> 6) * 7 + 3
    threshold = base << shifts
    token = _b64decode_urlsafe(token_str)
    buffer = bytearray(0x40000 * 0x30 + 0x4)  # 0xC00004
    for i in range(0x40000):
        idx = 0x4 + i * 0x30
        buffer[idx:idx + 0x30] = token

    while True:
        digest = hashlib.sha256(buffer).digest()
        view = struct.unpack('>I', digest[:4])[0]  # Big endian
        if view <= threshold:
            return f'1:{token_str}:{_b64encode_urlsafe(buffer[:4])}'

        # Increment the first 4 bytes as a little-endian integer
        for j in range(4):
            buffer[j] = (buffer[j] + 1) & 0xFF
            if buffer[j]:
                break

#
#
#########################################
