# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from enum import IntEnum

__all__ = ('LoginError', 'MegaErrorCodes', 'MegaNZError', 'RequestError', 'ValidationError')


class MegaErrorCodes(IntEnum):
    EINTERNAL = -1
    EARGS = -2
    EAGAIN = -3
    ERATELIMIT = -4
    EFAILED = -5
    ETOOMANY = -6
    ERANGE = -7
    EEXPIRED = -8
    ENOENT = -9
    ECIRCULAR = -10
    EACCESS = -11
    EEXIST = -12
    EINCOMPLETE = -13
    EKEY = -14
    ESID = -15
    EBLOCKED = -16
    EOVERQUOTA = -17
    ETEMPUNAVAIL = -18
    ETOOMANYCONNECTIONS = -19
    EWRITE = -20
    EREAD = -21
    EAPPKEY = -22
    MEGA_ERROR_CODE_GENERIC = -255

    def __str__(self) -> str:
        return f'{self.name} ({self.value:d})'


MEGA_ERROR_DESCRIPTION: dict[MegaErrorCodes, tuple[str, str]] = {
    MegaErrorCodes.EINTERNAL: ('EINTERNAL',
                               ('An internal error has occurred. Please submit a bug report, '
                                'detailing the exact circumstances in which this error occurred')),
    MegaErrorCodes.EARGS: ('EARGS', 'You have passed invalid arguments to this command'),
    MegaErrorCodes.EAGAIN: ('EAGAIN',
                            ('A temporary congestion or server malfunction prevented your request from being processed. '
                             'No data was altered. Retry')),
    MegaErrorCodes.ERATELIMIT: ('ERATELIMIT',
                                ('You have exceeded your command weight per time quota. Please wait a few seconds, then try again '
                                 '(this should never happen in sane real-life applications)')),
    MegaErrorCodes.EFAILED: ('EFAILED', 'The upload failed. Please restart it from scratch'),
    MegaErrorCodes.ETOOMANY: ('ETOOMANY', 'Too many concurrent IP addresses are accessing this upload target URL'),
    MegaErrorCodes.ERANGE: ('ERANGE', 'The upload file packet is out of range or not starting and ending on a chunk boundary'),
    MegaErrorCodes.EEXPIRED: ('EEXPIRED', 'The upload target URL you are trying to access has expired. Please request a fresh one'),
    MegaErrorCodes.ENOENT: ('ENOENT', 'Object (typically, node or user) not found'),
    MegaErrorCodes.ECIRCULAR: ('ECIRCULAR', 'Circular linkage attempted'),
    MegaErrorCodes.EACCESS: ('EACCESS', 'Access violation (e.g., trying to write to a read-only share)'),
    MegaErrorCodes.EEXIST: ('EEXIST', 'Trying to create an object that already exists'),
    MegaErrorCodes.EINCOMPLETE: ('EINCOMPLETE', 'Trying to access an incomplete resource'),
    MegaErrorCodes.EKEY: ('EKEY', 'A decryption operation failed (never returned by the API)'),
    MegaErrorCodes.ESID: ('ESID', 'Invalid or expired user session, please relogin'),
    MegaErrorCodes.EBLOCKED: ('EBLOCKED', 'User blocked'),
    MegaErrorCodes.EOVERQUOTA: ('EOVERQUOTA', 'Request over quota'),
    MegaErrorCodes.ETEMPUNAVAIL: ('ETEMPUNAVAIL', 'Resource temporarily not available, please try again later'),
    MegaErrorCodes.ETOOMANYCONNECTIONS: ('ETOOMANYCONNECTIONS', 'many connections on this resource'),
    MegaErrorCodes.EWRITE: ('EWRITE', 'Write failed'),
    MegaErrorCodes.EREAD: ('EREAD', 'Read failed'),
    MegaErrorCodes.EAPPKEY: ('EAPPKEY', 'Invalid application key; request not processed'),
    # fallback
    MegaErrorCodes.MEGA_ERROR_CODE_GENERIC: ('EGENERIC', 'Unknown error \'%d\''),
}


class MegaNZError(Exception):
    """Generic mega.nz error"""


class ValidationError(MegaNZError):
    """Error in validation stage"""


class LoginError(MegaNZError):
    """Error at login stage"""


class RequestError(MegaNZError):
    def __init__(self, msg_or_code: str | int | MegaErrorCodes) -> None:
        if isinstance(msg_or_code, (int, MegaErrorCodes)):
            self.code = msg_or_code
            if self.code in MEGA_ERROR_DESCRIPTION:
                err_name, err_desc = MEGA_ERROR_DESCRIPTION[self.code]
            else:
                err = MEGA_ERROR_DESCRIPTION[MegaErrorCodes.MEGA_ERROR_CODE_GENERIC]
                err_name = err[0]
                err_desc = err[1] % (self.code if isinstance(self.code, int) else self.code.value)
            self.message = f'{err_name}, {err_desc}'
        else:
            self.code = MegaErrorCodes.MEGA_ERROR_CODE_GENERIC
            self.message = str(msg_or_code)

    def __str__(self) -> str:
        return self.message

    __repr__ = __str__

#
#
#########################################
