# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from collections.abc import Generator, Sequence
from typing import NamedTuple

from Crypto.Cipher import AES
from Crypto.Util import Counter

from api.defs import CHUNK_BLOCK_LEN, DOWNLOAD_CHUNK_SIZE_INIT, DOWNLOAD_CHUNK_SIZE_MAX, EMPTY_IV
from api.encryption import pack_sequence, pad_bytes_end, unpack_sequence
from api.logging import Log

__all__ = ('make_chunk_decryptor', 'make_chunk_generator')


class Chunk(NamedTuple):
    offset: int
    size: int


def make_chunk_generator(chunk_size: int) -> Generator[Chunk]:
    # list of (offset, size), offset to file initial position
    offset = 0
    current_size = init_size = DOWNLOAD_CHUNK_SIZE_INIT
    while offset + current_size < chunk_size:
        yield Chunk(offset, current_size)
        offset += current_size
        if current_size < DOWNLOAD_CHUNK_SIZE_MAX:
            current_size += init_size
    yield Chunk(offset, chunk_size - offset)


def make_chunk_decryptor(iv: Sequence[int], k_decrypted: Sequence[int], meta_mac: tuple[int, ...]) -> Generator[bytes, bytes | None, None]:
    """
    Decrypts chunks of data received via `send()` and yields the decrypted chunks.
    It decrypts chunks indefinitely until a sentinel value (`None`) is sent.
    NOTE1: Initialize decryptor by requesting one chunk before interation 'next(chunker)'
    NOTE2: You MUST send `None` after decrypting every chunk to execute the mac check
    :param iv: Initialization vector (iv) as a list or tuple of two 32-bit unsigned integers
    :param k_decrypted: Decryption key as a tuple of four 32-bit unsigned integers
    :param meta_mac: The expected MAC value of the final file
    :returns decrypted chunk of data
    """
    try:
        k_bytes = pack_sequence(k_decrypted)
        counter = Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64)
        aes = AES.new(k_bytes, AES.MODE_CTR, counter=counter)

        # mega.nz uses CBC as a MAC mode: with each chunk the computed mac_bytes are used as iv for the next chunk MAC accumulation
        mac_bytes = EMPTY_IV
        mac_encryptor = AES.new(k_bytes, AES.MODE_CBC, mac_bytes)
        iv_bytes = pack_sequence([iv[0], iv[1], iv[0], iv[1]])
        raw_chunk = yield b''
        while True:
            if raw_chunk is None:
                break
            decrypted_chunk = aes.decrypt(raw_chunk)
            raw_chunk = yield decrypted_chunk
            encryptor = AES.new(k_bytes, AES.MODE_CBC, iv_bytes)

            # take last 16-N bytes from chunk (with N between 1 and 16, including extremes)
            mem_view = memoryview(decrypted_chunk)  # avoid copying memory for the entire chunk when slicing
            # ensure we reserve the last 16 bytes anyway, we have to feed them into mac_encryptor
            modchunk = (len(decrypted_chunk) % CHUNK_BLOCK_LEN) or CHUNK_BLOCK_LEN

            # pad last block to 16 bytes
            last_block = pad_bytes_end(mem_view[-modchunk:], amount=CHUNK_BLOCK_LEN)
            rest_of_chunk = mem_view[:-modchunk]
            _ = encryptor.encrypt(rest_of_chunk)
            input_to_mac = encryptor.encrypt(last_block)
            mac_bytes = mac_encryptor.encrypt(input_to_mac)

        file_mac = unpack_sequence(mac_bytes)
        computed_mac = file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]
        if computed_mac != meta_mac:
            Log.fatal(f'Mismatched mac (res {computed_mac!s} != meta {meta_mac!s})')
    except GeneratorExit:
        pass

#
#
#########################################
