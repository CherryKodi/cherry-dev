# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

from collections import defaultdict

from .base import _make_html_list
from .base import base_str
from .base import Result, ResultParam, MissingAttr
from .base import pats
from .msearch import dom_search

from .selectorparser import parse as parse_selector
from .selectorparser import Selector, AlternativeSelector, GroupSelector


# -------  DOM Select -------


def _select_desc(res, html, selectors_desc, sync=False):
    r"""
    Select descending tags "A B". Supports aternatives "{A, B}".

    Parameters
    res : list of str
        Result list, where found tags are appended.
    html : list of str
        List of input HTML parts.
    selectors_desc : list of str
        List of descending selectors. Each item can be aternativr list.
    sync : boll or Result.RemoveItem, default False
        if not False run dp,search in sync mode (returns None if not match).
    """
    part, tree, out_stack = html, None, []
    # Go through descending selector
    for single_selector in selectors_desc:
        #print('=======  SINGLE', single_selector)
        if isinstance(single_selector, list):
            assert isinstance(single_selector, AlternativeSelector)
            # subgroup of alterative nodes: " { A, B, ...} "
            subhtml = list(part if tree is None else tree)
            subpart = [part] if tree else []
            for sel in single_selector:
                #print('SEL-Alt', sel)
                res2 = []
                _select_desc(res2, subhtml, sel, sync=True)
                #print('mix!!! sh', subhtml)
                #print('mix!!! sr', res2)
                if not res2:
                    return
                subpart.append(res2)
            #print('---')
            #print('Mix!!! P', part)
            #print('MIX!!! S', subpart)
            # append as columns as rows
            part = list(p for p in zip(*subpart) if Result.RemoveItem not in p)
            #print('MIX!!! P', part)
            continue
        # single node selector
        #print('--- SINGLE', single_selector)
        assert isinstance(single_selector, Selector)
        sel = single_selector
        tree_last = False
        tag = '' if sel.tag == '*' else sel.tag
        # node id, class, attribute selectors or pseudoclasses (what to return)
        rsync = False if not sync else True if sel.optional else Result.RemoveItem
        nodefilter = (lambda n: all(f(n) for f in sel.nodefilterlist)) if sel.nodefilterlist else None
        if sel.result:
            #print(f'dom_search({part if tree is None else tree!r}, tag={tag!r}, ret={dict(attrs)}, sync={rsync}, separate=True)')
            part, tree = dom_search(part if tree is None else tree, tag, attrs=dict(sel.attrs),
                                    ret=ResultParam(sel.result, missing=MissingAttr.NoSkip,
                                                    separate=True, sync=rsync, nodefilter=nodefilter))
            if not tree:
                #print('PART', part, 'RETURN.')
                #print('TREE', tree, 'RETURN!')
                return []
            if part and not sel.optional:
                for i, v in enumerate(part):
                    if v == [ Result.RemoveItem ]:
                        part[i] = Result.RemoveItem
            if sel.result == [Result.NoResult]:
                part = None
            else:
                out_stack.append(part)
            tree_last = True
            #print('PART', list(zip(part, tree)))
            #res += list(zip(res, part))
        else:
            #print(f'dom_search({part if tree is None else tree!r}, tag={tag!r}, ret={dict(attrs)}, sync={rsync})')
            part, tree = dom_search(part if tree is None else tree, tag, attrs=dict(sel.attrs),
                                    ret=ResultParam(Result.Node, sync=rsync, nodefilter=nodefilter)), None
            if not part:
                #print('PART', part, 'RETURN!')
                #print('TREE', tree, 'RETURN.')
                return []
        #print('PART', part)
        #print('TREE', tree)
        #print('STACK', out_stack)
    #print('SelPART', part)
    #print('SelSTACK.1', out_stack)
    if part is None or len(out_stack) > 1 or (out_stack and not tree_last):
        if tree is None and part:
            out_stack.append(part)
        #print('SelSTACK.2', out_stack)
        #print('SelSTACK.3', list(zip(*out_stack)))
        res += list(zip(*out_stack))
    else:
        res += part
    return res


def _select_group(res, html, group_selector):
    # Go through alternative selector
    assert isinstance(group_selector, GroupSelector)
    for sel in group_selector:
        #print('SEL-ALT', sel)
        _select_desc(res, html, sel)


def dom_select(html, selectors):
    r"""
    Find data in HTML by CSS / jQuery simplified selector.

    Parameters
    ----------
    html : str or bytes or Node or DomMatch or list of str or list of bytes or list of Node
        HTML/XML source. Directly or list of HTML/XML parts.
    selectors : str or list of str
        Selector (or list of selectors).

    See CSS and jQuery selectors for base knowlage. This function support
    only a few selectors plus some extra extension.

    Supported selectors:
        - '*'          All elements
        - #id          The element with id
        - .class       All elements with class
        - tag          All <tag> elements
        - E1, E1       Or, all E1 and all E2 matched elements
        - E1 E2        Parent descendant, all E2 elements that are descendants of a E1 element
        - [attr]       All elements with a attribute `attr`
        - [attr=val]   All elements with a attribute value equal `val`
        - [attr^=val]  All elements with a attribute value starting with `val`
        - [attr$=val]  All elements with a attribute value ending with `val`
        - [attr~=val]  All elements with a attribute value containing word `val`
        - [attr|=val]  All elements with a attribute value containing word starting with`val`
        - [attr*=val]  All elements with a attribute value containing `val`

    Extra selectors:
        - { E1, E2 }     Alternative, E1 and/or E2 elements;
                         If some alternative doesn't exists None is returned.

    Pseudo elements are used to choise result:
        ::node      Returns Node(), it's default on last node
        ::content   Returns node content, e.g. 'A<b>B</b>'
        ::text      Returns note text (without tags), e.g. 'AB'
        ::attr(A)   Returns attribute `A`, comma separated list can be used
        (A)         Shortcut for ::attr(A)
        ::none      Do not return anything, but node has to exist
        ::DomMatch  Returns DomMatch nodes, for backward compability

    Examples
    --------

    >>> dom_select('<a>A</a>', 'a')
    [Node('A')]
    >>> dom_select('<a>A</a>', 'a::text')
    ['A']

    >>> dom_select('<a><b>Ba</b></a><z><b>Bz</b></z>', 'a b')
    [Node('Ba')]

    >>> dom_select('<a><b>B</b></a>', 'a { b, c? }')
    [(Node('Ba'), None)]
    >>> for b, c in dom_select('<a><b>B</b></a>', 'a { b, c? }'):
    >>>     print(b.text, 'no C' if c is None else c.text)

    >>> dom_select('<a x="1">A</a>', 'a(x)')
    [['1']]

    """
    # TODO   Selectors:
    # TODO   - [attribute!=value]
    # TODO   - A > B
    # TODO   - A + B
    # TODO   - fist, last, nth, etc.
    #
    #print(' --- search for "{}"'.format(selectors))
    ret = []
    if isinstance(selectors, base_str):
        ret = None
        selectors = [ selectors ]

    html = _make_html_list(html)

    # all selector from list
    for selgrp in selectors:
        selgrp = parse_selector(selgrp)
        # Go through alternative selector
        res = []  # All matches for single selector
        _select_group(res, html, selgrp)
        #print('RES', res)
        if ret == None:
            ret = res
        else:
            ret.append(res)
    return ret



if __name__ == '__main__':
    def printres(*args):
        print('\033[33;1m>\033[0m', *args, sep=' \033[33m|\033[0m ', end=' \033[33m|\033[0m\n')

    html = '<a x="11" y="12">A1<b>B1</b><c>C1</c></a> <a x="21" y="22">A2<b>B2</b><cc/></a>'

    for (a,), b, c in dom_select(html, 'a::node {b, c?}'):
        print(a.text, b.text, c and c.text)
    print('-')
    for row in dom_select(html, ':has(b)'):
        printres(row)
    print('-')
    for row in dom_select('<a x="1">A</a>', '[x]'):
        printres(row)

