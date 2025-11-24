# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import urllib.parse


def ensure_scheme_https(url: str) -> str:
    if urllib.parse.urlparse(url).scheme == 'http':
        return url.replace('http://', 'https://')

#
#
#########################################
