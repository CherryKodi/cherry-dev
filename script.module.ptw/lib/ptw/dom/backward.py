# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

from .base import Result, DomMatch
from .msearch import dom_search

def parseDOM(html, name=None, attrs=None, ret=None, exclude_comments=False):
    return dom_search(html, name, attrs=attrs,
                      ret=Result.Content if ret is None else ret,
                      exclude_comments=exclude_comments)

def parse_dom(html, name='', attrs=None, req=False, exclude_comments=False):
    return dom_search(html, name, attrs=attrs, ret=DomMatch,
                      exclude_comments=exclude_comments)


if __name__ == '__main__':
    print(parseDOM('<a>A</a>', 'a'))
