# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import re
from inspect import isclass

from .base import PY2
from .base import NoResult, Result, MissingAttr
from .base import regex, pats, remove_tags_re
from .base import _tostr, _make_html_list, find_node
from .base import Node, DomMatch



def find_closing(name, match, item, ms, me):
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
    int, int
        Content begin and content end offsets in `item`.

    """
    tag, ts, cs, ce, te = find_node(name, match, item, ms, me)
    return cs, ce


def dom_search(html, name=None, attrs=None, ret=None, exclude_comments=False):
    """
    Simple parse HTML/XML to get tags.

    Function parses HTML/XML, finds tags with attribites
    and returns matching tags content or attribute or Node().

    Paramters
    ---------
    html : str or bytes or Node or DomMatch or list of str or list of bytes or list of Node
        HTML/XML source. Directly or list of HTML/XML parts.
    name : str or bytes or None
        Tag name ot None if you want to match any tag. Can be regex string (e.g. "div|p").
    attr : dict or None
        Attributes to match or None if attributes has no matter. See below.
    ret : str or list of str or Node or DomMatch or False or None
        What to return. Tag content if False or None, Node or DomMatch nodes or attributes.
    exclude_comments : bool, default False
        If True, remove HTML comments before search.

    Returns
    -------
    list of str
        List of matched tags content (innerHTML) or matched attribute values if ret is used.
    list of Node
        List of mached nodes (attribute and content tuples) if ret is Node or Result.Node.
    list of DomMatch
        List of DomMatch mached nodes (attribute and content tuples) if ret is DomMatch or Result.DomMatch.

    """
    # Author: Robert Kalinowski <robert.kalinowski@sharkbits.com>
    #   Copyright (C) 2018 Robert Kalinowski
    # Idea is taken form parseDOM() by Tobias Ussing and Henrik Jensen.

    #print('dom_search: name="{name}", attrs={attrs}, ret={ret}'.format(**locals()))   # XXX DEBUG
    html = _make_html_list(html)

    if exclude_comments:
        # TODO: make it good, it's to simple, should ommit quotation in attribute
        re_comments = re.compile('<!--.*?-->', re.DOTALL)

    name = _tostr(name).strip()
    if not name or name == '*':
        name = pats.anyTag   # any tag

    class BreakAtrrLoop(Exception): pass

    # convert retrun item type to enum
    rtype2enum = {
        True:     Result.Node,
        False:    Result.Content,
        None:     Result.Content,
        Node:     Result.Node,
        DomMatch: Result.DomMatch,
    }
    #elif isclass(ritem) and issubclass(ritem, Node):
    #    ritem = Result.Node

    ret_lst, ret_nodes = [], []

    # Get details about expected result type
    try:
        separate = ret.separate
        sync = ret.sync
        skip_missing = ret.missing
        nodefilter = ret.nodefilter or (lambda n: True)
        ret = ret.args  # get requested ret
    except AttributeError:
        separate = sync = False
        skip_missing = MissingAttr.SkipIfDirect
        nodefilter = lambda n: True

    # Return list of values if ret is list  [a] -> [x]
    # otherwise return just values          a   -> x
    if isinstance(ret, (list, tuple)):
        retlstadd = ret_lst.append
        skip_missing = skip_missing == MissingAttr.SkipAll
        sync_none = [None if sync is True else sync]
    else:
        retlstadd, ret = ret_lst.extend, [ ret ]
        skip_missing = skip_missing != MissingAttr.NoSkip
        sync_none = None if sync is True else sync

    for ii, item in enumerate(html):
        if sync and item in (None, Result.RemoveItem):
            #print('search - None')
            ret_lst += [item]
            continue
        item = _tostr(item)
        if exclude_comments:
            item = re_comments.sub(item, '')
        if not item:
            continue

        lst = None
        try:
            for key, vals in (attrs or {None: None}).items():
                if not isinstance(vals, list):
                    vals = [ vals ]
                elif not vals:   # empty values means any value
                    vals = [ True ]
                for val in vals:
                    vkey = key
                    #print(f'-- key: {vkey!r}, val: "{val}"')
                    if key and val is None:  # Skip this attribute
                        vkey = None
                        #print(f'-> key: {vkey!r}, val: "{val}"')
                    #print('PAT', pats.melem(name, vkey, val))
                    lst2 = list(node
                                for r in re.finditer(pats.melem(name, vkey, val), item, re.DOTALL | re.IGNORECASE)
                                for node in (Node(tagstr=r.group(), tagindex=r.span(), item=item),)
                                if nodefilter(node))
                    #lst2 = list((r.group(), r.span()) for r in re.finditer(pats.melem(name, vkey, val), item, re.DOTALL | re.IGNORECASE))
                    #print(' L2', lst2)
                    #print(' L ', lst)
                    if lst is None:   # First match
                        lst = lst2
                    else:             # Delete anything missing from the next list.
                        matches = set(n.tagstr for n in lst2)
                        lst = list(n for n in lst if n.tagstr in matches)
                    if not lst:
                        if sync:
                            ret_lst.append(sync_none)
                            if separate:
                                ret_nodes.append(sync_none)
                        break
        except BreakAtrrLoop:
            pass
        if not lst:
            continue
        #print('LST', lst)

        for node in lst:
            #print('MATCH', match, matchIndex)
            lst2 = []
            if separate:
                ret_nodes.append(node)
            for ritem in ret:
                if PY2:
                    if type(ritem) is not int:
                        ritem = rtype2enum.get(ritem, ritem)
                else:
                    ritem = rtype2enum.get(ritem, ritem)
                #print('  -> ritem', ritem)
                if ritem == Result.Node:
                    # Get full node (content and all attributes)
                    lst2.append(node)
                elif ritem == Result.Content:
                    # Element content (innerHTML)
                    lst2.append(node.content)
                elif ritem == Result.OuterHTML:
                    # Get outerHTML - full element (tag and content)
                    lst2.append(node.outerHTML)
                elif ritem == Result.Text:
                    # Only text (remove all tags from content)
                    lst2.append(remove_tags_re.sub('', node.content))
                elif ritem == Result.DomMatch:
                    # Get old node (content and all attributes)
                    lst2.append(DomMatch(node.attrs, node.content))
                elif ritem == Result.NoResult:
                    # Match tag, but return nothing
                    lst2.append(NoResult())
                else:   # attribute
                    try:
                        lst2.append(node.attrs[ritem])
                    except KeyError:
                        if not skip_missing:
                            lst2.append(None)
            if lst2 or not skip_missing:
                retlstadd(lst2)

    if separate:
        return ret_lst, ret_nodes
    return ret_lst



def main():
    from .base import ResultParam
    from .base import aWord, aWordStarts, aStarts, aEnds, aContains

    def test_dom_search(html):
        r = dom_search(html, 'ul', {'class': 'a(?: c)?'})
        print(r)
        r1 = dom_search(r, 'a')
        print(r1)
        r2 = dom_search(r, 'a', ret='href')
        print(r2)
        print(list(zip(r1, r2)))
        print(dom_search(html, 'p', {'a': '1', 'b': '2'}))
        print(dom_search(html, 'p', {'a': [aWord('1'), aWord('2')]}))
        print(dom_search(html, 'p', {'a': [aWord('1'), aContains('2')]}))
        print(dom_search(html, 'p', {'a': aStarts('2')}))
        print(dom_search(html, 'p', {'a': aEnds('2')}))
        print(dom_search(html, 'p', {'a': aWordStarts('2')}))

    html = '''
    <ul class="a", data="vvv">
    <a href="a/a">Aa</a> qwe aaa
    <a href="a/b">Ab</a> asd aaa
    <a href="a/c">Ac</a> zxc aaa
    </ul>
    <ul class="b" data="nnn">
    <a href="b/a">Ba</a> qwe bbb
    <a href="b/b">Bb</a> asd bbb
    <a href="b/c">Bc</a> zxc bbb
    </ul>
    <ul class="a c", data="mmm">
    <a href="c/a">Ca</a> qwe ccc
    <a href="c/b">Cb</a> asd ccc
    <a href="c/c">Cc</a> zxc ccc
    </ul>
    <p a="1" b="2">12a</p>
    <p b="2" a="1">12b</p>
    <p a="1">12-c</p>
    <p b="2">12-d</p>
    <p c="3" e="żółć">12-<b>33</b>-e</p>
    <div c="3">12-<b>33</b>-e</div>
    <p a="1 2 3">1.2.3</p>
    <p a="1 22 3">1.22.3</p>
    <p a="22 1 3">22.1.3</p>
    <p a="1 3 22" b=42>1.3.22</p>
    <p a="1 020 3">1.020.3</p>
    <p a="1 022 3">1.022.3</p>
    <p a="1 220 3">1.220.3</p>
    <div a="1 22 3" c="44">1.22.3</div>
    <div a="22 1 3" c="45">22.1.3</div>
    <div c="4">c4..<b z="9">bz9</b></div>
    <div
     c="5"
     d="<b>BB</b>">
     c4..
     <b
      z="0">
      bz0
     </b>
    </div>
    '''

    #exit()

    #test_dom_search(html)
    print(' - - - - -')
    #test_dom_select(html)
    #print(dom_select('<a>A1</a><a>A2</a><b>B1</b><b>B2</b>', 'a'))
    #print(dom_select('<a>A1</a><a>A2</a><b>B1</b><b>B2</b>', ['a', 'b']))
    #print(dom_select('<a x=1><b y=2>B</b></a>', 'a::attr(x) b::attr(y)'))
    print(dom_search('<a x=1><b y=2 z=3>B</b></a>', 'a', ret=False))
    print(dom_search('<a x=1><b y=2 z=3>B</b></a>', 'a', ret='x'))
    print(dom_search('<a x=1><b y=2 z=3>B</b></a>', 'a', ret=['x']))
    print(dom_search('<a x=1><b y=2 z=3>B</b></a>', 'b', ret=['y', 'z']))

    #print(dom_search('<a x=11>A11<b y=12 z=13>B1</b>A12</a><a x=21>A21<b y=22 z=23>B2</b>A22</a>',
    #                 'a',
    #                 ret=ResultParam(['x', 'y', 'z', Result.Text])
    #                 #ret='x'
    #                 ))

    #print(dom_search(['<a x="1">A</a><a>B</a>', '<a x="2">A</a><a>B</a>'], 'a', {}, ret='x'))
    #print(dom_search(['<a x="1">A</a><a>B</a>', '<a x="2">A</a><a>B</a>'], 'a', {}, ret=['x']))
    #print(dom_search(['<a x="1">A</a><a>B</a>', '<a x="2">A</a><a>B</a>'], 'a', {}, ret=ResultParam(['x'], separate=True)))

    #print(_split_selector('A { B, C D {E, F}}, Z'))

    'ul.dropdown-menu { a::attr(href), img::attr(src:"/(?P<name>.*?)\.[^.]*$") }'
    'ul.dropdown-menu { a::attr(href), img::attr(src) }'

    def printres(*args):
        print('\033[33;1m>\033[0m', *args, sep=' \033[33m|\033[0m ', end=' \033[33m|\033[0m\n')


if __name__ == '__main__':
    main()
