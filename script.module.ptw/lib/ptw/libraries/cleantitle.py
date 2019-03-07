# -*- coding: utf-8 -*-

"""
    Covenant Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import unicodedata


def get(title):
    if title is None: return
    try:
        title = title.encode('utf-8')
    except:
        pass
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|–|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title


def geturl(title):
    if title is None: return
    title = title.lower()
    title = title.translate(None, ':*?"\'\.<>|&!,')
    title = title.replace('/', '-')
    title = title.replace(' ', '-')
    title = title.replace('--', '-')
    return title


def get_simple(title):
    if title is None: return
    title = title.lower()
    title = re.sub('(\d{4})', '', title)
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|\(|\)|\[|\]|\{|\}|\s(vs|v[.])\s|(:|;|-|–|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title


def getsearch(title):
    if title is None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|/|!|\[|\]|-|–|:|;|\*|\?|"|\'|<|>|\|', '', title).lower()
    title = title.replace("."," ").replace("  "," ")
    return title


def query(title):
    if title is None: return
    title = title.replace('\'', '').rsplit(':', 1)[0].rsplit(' -', 1)[0].replace('-', ' ')
    return title


maketrans = lambda s1, s2: dict(zip(map(ord, s1), map(ord, s2)))
unicode_translate_table = maketrans(u'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ–—\u2044•„”«»', u'acelnoszzACELNOSZZ--/.""<>')

def normalize(title):
    """Convert UTF-8 title to ASCII as well as we can."""
    if not isinstance(title, type(u'')):
        title = title.decode('utf-8')
    try:
        title = u''.join(c for c in unicodedata.normalize('NFKD', title)
                         if unicodedata.category(c) != 'Mn')
    except:
        pass
    return title.translate(unicode_translate_table).encode('ascii', 'replace')


def clean_search_query(url):
    url = url.replace('-','+')
    url = url.replace(' ', '+')
    return url
