# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import urllib.parse

HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
SITE_PRIMARY = f'{HTTPS_PREFIX}mega.nz'
SITE_API = f'{HTTPS_PREFIX}g.api.mega.co.nz/cs'


def ensure_scheme_https(url: str) -> str:
    if urllib.parse.urlparse(url).scheme == 'http':
        return url.replace(HTTP_PREFIX, HTTPS_PREFIX)


def compose_link_v2(folder_id: str, file_id: str, key: str) -> str:
    """
    :param folder_id: [str] mega folder id (if any)
    :param file_id: [str] mega file id (if any)
    :param key: [str] mega decryption key
    :returns: composed file OR folder OR folder file link (version 2)
    """
    if key and (folder_id or file_id):
        if folder_id:
            link = f'{SITE_PRIMARY}/folder/{folder_id}#{key}'
            if file_id:
                link = f'{link}/file/{file_id}'
        else:  # if file_id
            link = f'{SITE_PRIMARY}/file/{file_id}#{key}'
        return link
    # invalid link always
    return ''

#
#
#########################################
