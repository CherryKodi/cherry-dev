# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

from collections import defaultdict

from .base import aWord, aWordStarts, aStarts, aEnds, aContains
from .base import s_attrSelectors, s_resSelectors, pats, regex
from .base import Node, DomMatch, Result


from arpeggio import Optional, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as R
from arpeggio import NonTerminal, Terminal
from arpeggio import ParserPython, PTNodeVisitor, visit_parse_tree


DEBUG = False


# --- DOM Selector Grammar ---
def space():       return R(r'\s+')   # must be a space
def sp():          return R(r'\s*')   # can be a space
SP = Optional(sp)
def ident():       return R(r'[\w-]+')
def val():         return [ ("'", R(r"[^']*"), "'"), ('"', R(r'[^"]*'), '"'), R(r'''[\w-]+''') ]
ZeroOrMoreValBr    = [("(", SP, val, ZeroOrMore(SP, ",", SP, val), SP, ")"), ("(", SP, ")")]
def tag():         return [ ident, "*" ]
def opt_tag():     return '?'
def id_sel():      return '#', ident
def class_sel():   return '.', ident
def attr_op():     return R('[$^~|*]?=')
def attr_sel():    return '[', ident, Optional(attr_op, val), ']'
def pseudo_sel():  return ':', ident, Optional(ZeroOrMoreValBr)
def param_sel():   return [ id_sel, class_sel, attr_sel, pseudo_sel ]
def res_attr():    return "(", SP, val, ZeroOrMore(SP, ",", SP, val), SP, ")"
def res_param():   return "::", ident, Optional(ZeroOrMoreValBr)
def one_sel():     return [ (tag, Optional(opt_tag), ZeroOrMore(param_sel)), OneOrMore(param_sel) ], Optional(res_attr), ZeroOrMore(res_param)
def alt_sel():     return "{", SP, desc_sel, ZeroOrMore(SP, ",", SP, desc_sel), SP, "}"
def single_sel():  return [ one_sel, alt_sel ]
def desc_sel():    return single_sel, ZeroOrMore(space, single_sel)
def selector():    return desc_sel, ZeroOrMore(SP, ",", SP, desc_sel), EOF


#: DOM selector parser.
parser = ParserPython(selector, skipws=False, debug=False)


def dump(tree, lvl=0, path=None):
    r"""Dump Arpeggio tree."""
    #print(type(tree))
    #path = (path or []) + [tree.rule_name or '']
    print('{:{}} {}.\033[33m{}\033[0m '.format('', lvl+1, '.'.join(path or ()), tree.rule_name), end='')
    path = (path or []) + [tree.rule_name or '']
    if isinstance(tree, NonTerminal):
        print(':')
        for it in tree:
            dump(it, lvl + 1, path)
    else:
        print(' = >>>\033[1;44m{}\033[0m<<<'.format(tree.value))


class Selector(object):
    r"""Single selector (tag, attributes, psudo-elements etc.)."""
    def __init__(self, tag=None, param=None, result=None):
        self.tag = tag or ''
        self.optional = False
        self.attrs, self.result, self.nodefilterlist = defaultdict(lambda: []), [], []
        self.param = param or []

class GroupSelector(list):
    r"""Main group selector (A, B)."""

class DescendSelector(list):
    r"""Descending selector (A B)."""

class AlternativeSelector(list):
    r"""Alternative selector ( {A, B} )."""


class SelectorBuilder(object):
    r"""
    Build selector structure for dom_select().

    Parameters
    ----------
    tree
        Arpeggio parsed tree.
    """

    # TODO:  Exception from one base

    def __init__(self, tree):
        self.tree = tree
        self.skip = {'sp'}
        self.stack, self.out = [], GroupSelector()
        self.cur = self.out
        self._cur_ident = self._cur_attr_op = self._cur_val = None
        self._cur_vals = []

    @property
    def sel(self):
        return self.cur[-1]

    def _build(self, item, lvl=0, path=None, parent=None):
        name = item.rule_name or ''
        cname = '.'.join((parent or '', name))
        path = (path or []) + [item.rule_name or '']
        if isinstance(item, NonTerminal):
            if not name in self.skip:
                self.enter(name, parent, item)
            for it in item:
                self._build(it, lvl + 1, path, name)
            if not name in self.skip:
                self.exit(name, parent, item)
        else:
            if not name in self.skip:
                self.terminal(name, parent, item.value)

    def build(self):
        self._build(self.tree)

    def _list_enter(self, lst=None):
        new = [] if lst is None else lst
        self._list_append(new)
        self.stack.append(self.cur)
        self.cur = new

    def _list_exit(self):
        self.cur = self.stack.pop()

    def _list_append(self, s):
        self.cur.append(s)
        #if True:
        #    self.cur.append([s])
        #else:
        #    self.cur[-1].append(s)

    def enter(self, name, parent, children):
        if DEBUG and __name__ == '__main__':
            print('Entering Token', name)
        if name == 'desc_sel':
            self._list_enter(DescendSelector())
        elif name == 'alt_sel':
            self._list_enter(AlternativeSelector())
        elif name == 'one_sel':
            self._list_append(Selector())
        elif name == 'val':
            val = children[:2][-1].value
            if not self._cur_vals:
                self._cur_val = val
            self._cur_vals.append(val)

    def exit(self, name, parent, children):
        if DEBUG and __name__ == '__main__':
            print('Exiting Token', name)
        if name == 'desc_sel':
            self._list_exit()
        elif name == 'alt_sel':
            self._list_exit()
        elif name == 'attr_sel':
            assert self._cur_ident is not None
            try:
                self.sel.attrs[self._cur_ident].append(s_attrSelectors[self._cur_attr_op](self._cur_val))
            except KeyError:
                raise KeyError('Attribute selector "{op}" is not supported'.format(op=self._cur_val))
        elif name == 'pseudo_sel':
            assert self._cur_ident is not None
            try:
                fun = getattr(self, '_pseudo_' + self._cur_ident.replace('-', '_'))
            except AttributeError:
                raise KeyError('Pseudo-class "{op}" is not supported'.format(op=self._cur_ident))
            self.sel.nodefilterlist.append(fun(self._cur_val))
        elif (name == 'res_param' and self._cur_ident == 'attr') or name == 'res_attr':
            if not self._cur_vals:
                raise IndexError('::attr() needs at least one attribute name')
            self.sel.result += self._cur_vals
        elif name == 'res_param':
            assert self._cur_ident is not None
            try:
                self.sel.result.append(s_resSelectors[self._cur_ident])
            except:
                raise KeyError('Pseudo-elem (result param) "{}" is not supported'.format(self._cur_ident))

    def terminal(self, name, parent, value):
        cname = '.'.join((parent or '', name))
        if DEBUG and __name__ == '__main__':
            print('Token Value {} = {!r}  ({})'.format(name, value, cname))
        if not name and value == '(':
            self._cur_val, self._cur_vals = None, []
        elif name == 'tag' or cname in ('tag.ident', 'tag.'):
            self.sel.tag = value
        elif name == 'opt_tag':
            self.sel.optional = bool(value)
        elif cname == 'id_sel.ident':
            self.sel.attrs['id'].append(value)
        elif cname == 'class_sel.ident':
            self.sel.attrs['class'].append(aWord(value))
        elif name == 'ident':
            self._cur_ident, self._cur_attr_op = value.lower(), None
            self._cur_val, self._cur_vals = None, []
        elif cname == 'attr_sel.attr_op':
            self._cur_attr_op = value

    def _pseudo_contains(self, value):
        def nodefilter(n, arg=value):
            return arg in n.text
        return nodefilter

    def _pseudo_content_contains(self, value):
        def nodefilter(n, arg=value):
            return arg in n.content
        return nodefilter

    def _pseudo_regex(self, value):
        rx = regex(value)
        def nodefilter(n, rx=rx):
            return rx.search(n.outerHTML)
        return nodefilter

    def _pseudo_has(self, value):
        # TODO:  Fix: :has(c) in "<b z="<c>">"
        rx = regex(pats.melem(value, None, None))
        def nodefilter(n, rx=rx):
            return rx.search(n.content)
        return nodefilter

    def _pseudo_empty(self, value):
        return lambda n: not n.content



def parse(sel):
    r"""Parse selector `sel` and return structure for dom_select()."""
    tree = parser.parse(sel)
    #dump(tree)
    #pprint(build(tree))
    builder = SelectorBuilder(tree)
    builder.build()
    return builder.out


def set_debug_repr():
    GroupSelector.__repr__ = lambda self: '\033[36mG\033[0m' + list.__repr__(self)
    DescendSelector.__repr__ = lambda self: '\033[36mD\033[0m' + list.__repr__(self)
    AlternativeSelector.__repr__ = lambda self: '\033[36mA\033[0m' + list.__repr__(self)
    #Selector.__repr__ = lambda self: '\033[36mS\033[0;2m(\033[0;4m{}{},{},F#{},{}\033[0;2m)\033[0m'.format(
    Selector.__repr__ = lambda self: '\033[36mS\033[0m(\033[0;2m{}{},{},F#{},{}\033[0m)\033[0m'.format(
        self.tag, self.optional and '?' or '', dict(self.attrs),
        len(self.nodefilterlist), self.result)


if __name__ == '__main__':
    import os.path
    import sys
    import argparse
    import pprint
    pprint = pprint.PrettyPrinter(indent=2).pprint

    aparser = argparse.ArgumentParser()
    aparser.add_argument('selectors', metavar='SEL', nargs='+', help='selector to parse')
    aparser.add_argument('--debug', action='store_true', help='debug info')
    args = aparser.parse_args()
    #print(args)

    if args.debug:
        DEBUG = True

    # parse("a[x~='3']:x()::attr(q)")
    for sel in args.selectors:
        print("- - - - -")
        print(parse(sel))



