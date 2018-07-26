# -*- coding: UTF-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import re


class RegExMatchIter(object):
    r"""
    Helper. RegEx iterator.
    """

    __slots__ = ('_match', '_first')

    def __init__(self, match):
        self._match = match
        self._first = True

    def __next__(self):
        if self._first:
            self._first = False
        else:
            match = self._match
            self._match = self._match.re.search(match.string, match.end())
        if not self._match:
            raise StopIteration
        return RegExMatch(self._match)

    next = __next__  # Python2



class RegExMatch(object):
    r"""
    Shortcut for standard re module.

    Parameters
    ----------
    pat : str
        RegEx pattern.
    """

    __slots__ = ('_match', '_re', '_values')

    def __init__(self, match, re=None):
        self._match = match
        if match:
            self._re, self._values = re or match.re, match.groupdict()
        else:
            self._re, self._values = re, {}

    @property
    def match(self):
        return self._match

    def _default(self, key, error):
        raise error('No key {} in regex'.format(key))

    def _get_value(self, key, error):
        try:
            return self._values[key]
        except KeyError:
            if self._re and key in self._re.groupindex:
                return None
            return self._default(key, error)

    def __getitem__(self, key):
        r"""Get by group re_match[1], get by name re_match[name]."""
        if isinstance(key, int):
            try:
                return self._match.group(key)
            except IndexError:
                return self._default(key, KeyError)
        return self._get_value(key, KeyError)

    def __getattr__(self, key):
        r"""Get by name re_match.name."""
        return self._get_value(key, AttributeError)

    def __bool__(self):
        return bool(self._match)

    __nonzero__ = __bool__  # Python2

    def keys(self):
        return len(self._values)

    def __iter__(self):
        return RegExMatchIter(self._match)



class RegEx(object):
    r"""
    Shortcut for standard re module.

    Parameters
    ----------
    pat : str
        RegEx pattern.
    flags : int
        Regex or-ed flags.

    Examples
    --------

    >>> RegEx('a(?P<b>b+)c')('abbbc').b
    'bbb'

    >>> regex = RegEx('a(?P<b>b+)c')
    >>> for match in regex('abbbc abbc'):
    >>>     print(match.b)
    bbb
    bb

    """

    __slots__ = ('_re')

    def __init__(self, pat, flags=None):
        if flags is None:
            flags = re.DOTALL
        self._re = re.compile(pat, flags)

    @property
    def pattern(self):
        return self._re.re.pattern

    @property
    def re(self):
        return self._re

    def __call__(self, source):
        return RegExMatch(self.re.search(source), self._re)


#return =re_chann_name.search(src).groupdict('chan')

if __name__ == '__main__':
    print(RegEx('a(?P<b>b+)c')('abbbc').b)
    regex = RegEx('a(?P<b>b+)c')
    for match in regex('abbbc abbc'):
        print(match.b)
    print(bool(RegEx('a(?P<b>b+)c')('azzzc')))
    print(RegEx('a(?P<b>b+)c')('azzzc').b)
    try:
        print(RegEx('a(?P<b>b+)c')('azzzc').c)
    except AttributeError:
        print('Expected AttributeError (there is no "c" in regex)')

