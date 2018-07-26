# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import sys
import re
from collections import defaultdict
from collections import namedtuple
try:
    from requests import Response
except ImportError:
    Response = None

PY2 = sys.version_info < (3,0)

if PY2:
    type_str, type_bytes, base_str = unicode, str, basestring
    class Enum: pass
else:
    type_str, type_bytes, unicode, base_str = str, bytes, str, str
    from enum import Enum


class NoResult(list):
    __slots__ = ()
    def __init__(self):
        super(NoResult, self).__init__()
    def append(self, v):
        raise NotImplementedError('NoResult is readonly')
    def extend(self, v):
        raise NotImplementedError('NoResult is readonly')
    def __setitem__(self, key, val):
        raise NotImplementedError('NoResult is readonly')
    # TODO: all methods



# TODO move to separate module
class AttrDict(dict):
    """dict() + attribute access"""
    # Note: it's match slower than dict(): 480 ns vs. 40 ns

    __slots__ = ()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('AttrDict has no attribute "{}"'.format(key))

    def __setattr__(self, key, value):
        self[key] = value


# TODO move to separate module
class RoAttrDictView(object):
    r"""
    Read only, attribute only view of given dict.

    Parameters
    ----------
    """

    __slots__ = ('__mapping', '__fmt')

    def __init__(self, mapping, fmt=None):
        self.__mapping = mapping
        self.__fmt = fmt

    def __getattr__(self, key):
        if self.__fmt is not None:
            key = self.__fmt.format(key)
        try:
            return self.__mapping[key]
        except KeyError:
            raise AttributeError('RoAttrDictView of {} has no attribute "{}"'.format(
                self.__mapping.__class__.__name__, key))

    def __call__(self, key):
        return getattr(self, key)



regex = re.compile


class Patterns(object):
    """All usefull patterns"""
    def __init__(self):
        self._dict = {}
        pats = self
        pats.anyTag       = r'''[\w-]+'''
        pats.anyAttrVal   = r'''(?:=(?:[^\s/>'"]+|"[^"]*?"|'[^']*?'))?'''
        pats.askAttrVal   = r'''(?:=(?:(?P<val1>[^\s/>'"]+)|"(?P<val2>[^"]*?)"|'(?P<val3>[^']*?)'))?'''
        pats.anyAttrName  = r'''[\w-]+'''
        pats.askAttrName  = r'''(?P<attr>[\w-]+)'''
        pats.anyAttr      = r'''(?:\s+{anyAttrName}{anyAttrVal})*'''.format(**pats)
        pats.mtag         = lambda n: r'''(?:{n})(?=[\s/>])'''.format(n=n)
        pats.mattr        = lambda n, v: \
                r'''(?:\s+{attr}{anyAttrVal})'''.format(attr=n, **pats) \
                if v is True else \
                r'''\s+{n}(?:=(?:{v}(?=[\s/>])|"{v}"|'{v}'))'''.format(n='(?:{})'.format(n), v='(?:{})'.format(v or ''))
        pats.melem        = lambda t, a, v: \
            r'''<{tag}(?:\s+(?!{attr}){anyAttrName}{anyAttrVal})*\s*/?>'''.format(tag=pats.mtag(t), attr=a, **pats)  \
            if a and v is False else \
            r'''<{tag}{anyAttr}{attr}{anyAttr}\s*/?>'''.format(tag=pats.mtag(t), attr=pats.mattr(a, v), **pats)  \
            if a else \
            r'''<{tag}{anyAttr}\s*/?>'''.format(tag=pats.mtag(t), **pats)
        pats.getTag       = r'''<([\w-]+(?=[\s/>]))'''
        pats.openCloseTag = '(?:<(?P<beg>{anyTag}){anyAttr}\s*>)|(?:</(?P<end>{anyTag})\s*>)'.format(**pats)
        pats.nodeTag = '(?:<(?P<beg>{anyTag}){anyAttr}(?:\s*(?P<slf>/))?\s*>)|(?:</(?P<end>{anyTag})\s*>)'.format(**pats)

        #: Find alternatives with subgroups.
        pats.sel_alt_re = re.compile(r'''\s*((?:\(.*?\)|".*?"|[^,{}\s+>]+?)+|[,{}+>])\s*''')
        #: Find single tag (with params).
        pats.sel_tag_re = re.compile(r'''(?P<tag>\w+)(?P<optional>\?)?(?P<attr1>[^\w\s](?:"[^"]*"|'[^']*'|[^"' ])*)?|(?P<attr2>[^\w\s](?:"[^"]*"|'[^']*'|[^"' ])*)''')
        #: Find params (id, class, attr and pseudo).
        pats.sel_attr_re = re.compile(
            r'''#(?P<id>[^[\s.#]+)|\.(?P<class>[\w-]+)|\[(?P<attr>[\w-]+)''' \
            r'''(?:(?P<aop>[~|^$*]?=)(?:"(?P<aval1>[^"]*)"|'(?P<aval2>[^']*)'|(?P<aval0>(?<!['"])[^]]+)))?''' \
            r'''\]|(?P<pseudo>::?[-\w]+)(?:\((?P<psarg1>.*?)\))?''')

    def __setattr__(self, key, val):
        super(Patterns, self).__setattr__(key, val)
        if not key.startswith('_'):
            self._dict[key] = val

    def __getitem__(self, key):
        return self._dict[key]

    def keys(self):
        return self._dict.keys()


class Regex(AttrDict):
    """All usefull regex (compiled patterns)."""
    def __init__(self, pats):
        self.__pats = pats
    def __missing__(self, key):
        pat = self.__pats[key]
        if isinstance(pat, base_str):
            self[pat] = re.compile(pat, re.DOTALL)
            return self[pat]
        raise KeyError('No regex "{}"'.format(key))



pats = Patterns()
regs = Regex(pats)   # not used now
remove_tags_re = re.compile(pats.nodeTag)
openCloseTag_re = re.compile(pats.openCloseTag, re.DOTALL)


class DomMatch(namedtuple('DomMatch', ['attrs', 'content'])):
    __slots__ = ()

    @property
    def text(self):
        return remove_tags_re.sub('', self.content)


class Result(Enum):
    NoResult = 0
    Content = 1
    Node = 2
    Text = 3
    InnerHTML = Content
    OuterHTML = 4
    DomMatch = 91

    # --- internals ---
    RemoveItem = 'REMOVE'


class MissingAttr(Enum):
    #: Do not skip any attribures, return None if missing.
    NoSkip = 0
    #: Skip only if attribute was direct requested (e.g. for 'a')
    #: else return None (e.g. for ['a']).
    SkipIfDirect = 1
    #: Skipp all missing attributes.
    SkipAll = 2


class ResultParam(object):
    r"""
    Helper to tell dom_search() more details about result.

    Parameters
    ----------
    args : str or list of str
        Object or list of object (e.g. attributes) in result.
    separate : bool, default False
        If true dom_search() return content and values separated.
    missing
        How to handle missing attributes, see MissingAttr.
    sync : bool or Result.RemoveItem
        If True result caontains None (or Result.RemoveItem) if not match
        If False result contains only matching items.
    nodefilter : callable or None
        Filter found nodes: nodefilter(node) -> bool.
        If filter function returns False node will be skipped.
    """
    def __init__(self, args,
                 separate=False,
                 missing=MissingAttr.SkipIfDirect,
                 sync=False,
                 nodefilter=None):
        self.args = args
        self.separate = separate
        self.missing = missing
        self.sync = sync
        self.nodefilter = nodefilter


def aWord(s):
    '''Realize [attribute~=value] selector'''
    return'''[^'"]*?(?<=['" ]){}(?=['" ])[^'"]*?'''.format(s)

def aWordStarts(s):
    '''Realize [attribute|=value] selector'''
    return'''[^'"]*?(?<=['" ]){}[^'"]*?'''.format(s)

def aStarts(s):
    '''Realize [attribute^=value] selector'''
    return'''(?<=['"]){}[^'"]*?'''.format(s)

def aEnds(s):
    '''Realize [attribute$=value] selector'''
    return'''[^'"]*?{}(?=['"])'''.format(s)

def aContains(s):
    '''Realize [attribute*=value] selector'''
    return '''[^'"]*?{}[^'"]*?'''.format(s)


def _tostr(s):
    """Change bytes to string (also in list)"""
    if isinstance(s, Node):
        s = s.content
    if isinstance(s, DomMatch):
        s = s.content
    elif isinstance(s, (list, tuple)):
        return list(_tostr(z) for z in s)
    if s is None or s is False or s is True:
        s = ''
    elif isinstance(s, type_bytes):
        try:
            s =  s.decode("utf-8")
        except:
            pass
    elif not isinstance(s, base_str):
        s = str(s)
    return s


def _make_html_list(html):
    r"""Helper. Make list of HTML part."""
    if Response and isinstance(html, Response):
        html = html.text
    if isinstance(html, DomMatch) or not isinstance(html, (list, tuple)):
        html = [ html ]
    return html


def find_node(name, match, item, ms, me):
    r"""
    Helper. Find closing tag for given `name` tag.

    Parameters
    ----------
    name : str
        Tag name (name or regex pattern, can be e.g. '.*').
    match : str
        Found full tag string (tag with attributes).
    item : str
        Original HTML string or HTML part string.
    ms : int
        Offset in `item` for `match`.
    me : int
        Offset in `item` for `match` end.

    Returns
    -------
    ts : int
        Tag start ('<') index in `item`.
    cs : int
        Content start index in `item`.
        It's also tag end (one characteter after '>') index.
    ce : int
        Content end index in `item`.
        It's also closing tag start ('</') index.
    te : int
        Closing tag end index (one characteter after closing '>') in `item`.

    Function returns index of parsed node:

        <tag attr="val">content</tag>
        ↑               ↑      ↑     ↑
        ts              cs     ce    te

    item[ts:cs] -- tag
    item[cs:ce] -- content, innerHTML
    item[ce:te] -- closing tag
    item[ts:te] -- whole tag, outerHTML
    """
    # Recover tag name (important for "*")
    r = re.match(pats.getTag, match, re.DOTALL)
    tag = r.group(1) if r else name or '[\w-]+'
    # <tag/> has no content
    if match.endswith('/>'):
        return tag, ms, me, me, me
    # find closing tag
    ce = ee = me
    tag_stack = [ tag ]
    #for r in re.compile(pats.openCloseTag, re.DOTALL).finditer(item, me):
    #for r in regs.openCloseTag.finditer(item, me):
    for r in openCloseTag_re.finditer(item, me):
        d = r.groupdict()
        if d['beg']:
            tag_stack.append(d['beg'])
        elif d['end']:
            while tag_stack:
                last = tag_stack.pop()
                if last == d['end']:
                    break
            if not tag_stack:
                ce, ee = r.start(), r.end()
                break;
    return tag, ms, me, ce, ee


class Node(object):
    r"""
    XML/HTML simplified node. Without structure.

    Parameters
    ----------
    tag : str
        Tag string (e.g. '<tag attr="val">'.
    item : str or None
        Part of HTML string containg this node.
    """

    __slots__ = ('ts', 'cs', 'ce', 'te',
                 'item', '__name', 'tagstr',
                 '__attrs',
                 #'__content',
                 #'__vals',
                 )

    def __init__(self, tagstr, item=None, tagindex=None):
        self.ts = self.cs = self.ce = self.te = 0
        self.tagstr = tagstr
        self.item = item or ''
        self.__name = None
        self.__attrs = None
        if tagindex is not None:
            self.ts, self.cs = tagindex

    def _preparse(self, item=None, tagindex=None, tagname=None):
        r"""
        Preparsing node. Find closing tag for given `name` tag.

        item : str
            Original HTML string or HTML part string.
        ms : int
            Tag ('<') index in `item`.
        me : int
            End of tag (one characteter after '>') index in `item`.
        tagname : str or None
            Tag name (name or regex pattern, can be e.g. '.*').

        See find_node().
        """
        ms, me = (self.ts, self.cs) if tagindex is None else tagindex
        if item is None:
            item = self.item
        self.__name, self.ts, self.cs, self.ce, self.te = find_node(tagname, self.tagstr, item, ms, me)
        return self

    @property
    def attrs(self):
        r"""Returns parsed attributes."""
        if self.__attrs is None:
            self.__attrs =  dict((attr.lower(), a or b or c) \
                                 for attr, a, b, c in \
                                 re.findall(r'\s+{askAttrName}{askAttrVal}'.format(**pats),
                                            self.tagstr, re.DOTALL))
        return self.__attrs

    @property
    def content(self):
        r"""Returns tag content (innerHTML)."""
        if not self.te:
            self._preparse()
        return self.item[self.cs : self.ce]

    innerHTML = content

    @property
    def outerHTML(self):
        r"""Returns tag with content (outerHTML)."""
        if not self.te:
            self._preparse()
        return self.item[self.ts : self.te]

    @property
    def text(self):
        r"""Returns tag text only."""
        return remove_tags_re.sub('', self.content)

    @property
    def name(self):
        r"""Returns tag name."""
        if self.__name is None:
            r = re.match(pats.getTag, self.tagstr or '', re.DOTALL)
            if r:
                self.__name = r.group(1)
        return self.__name or ''

    @property
    def attr(self):
        r"""Returns attribute only access to node attributes."""
        return RoAttrDictView(self.attrs)

    @property
    def data(self):
        r"""Returns attribute only access to node custom attributes (data-*)."""
        return RoAttrDictView(self.attrs, fmt='data-{}')

    def __str__(self):
        return self.content

    def __repr__(self):
        return 'Node({name!r}, {attrs}, {content!r})'.format(
            name=self.name, attrs=self.attrs, content=self.content)



# -------  DOM Select -------

#: Attribute selector operation.
s_attrSelectors = {
    None:  lambda v: True,
    '=':   lambda v: v,
    '~=':  aWord,
    '|=':  aWordStarts,
    '^=':  aStarts,
    '$=':  aEnds,
    '*=':  aContains,
}

#: Result param pseudo-element (::xxx)
s_resSelectors = {
    'content':   Result.Content,
    'node':      Result.Node,
    'text':      Result.Text,
    'DomMatch':  Result.DomMatch,
    'none':      Result.NoResult,
    'innerHTML': Result.InnerHTML,
    'outerHTML': Result.OuterHTML,
}

