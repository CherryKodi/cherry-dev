# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

from .base import TestCase
from unittest import skip as skiptest, skipIf as skiptestIf

#from ..dom import _split_selector


# TODO;  change _split_selector to dom.selectorparser.parse

#class TestDomSearchSplitselector(TestCase):
#
#    def test_base(self):
#        self.assertEqual(_split_selector(''), [])
#        self.assertEqual(_split_selector('A'), [['A']])
#
#    def test_alt(self):
#        self.assertEqual(_split_selector('A'), [['A']])
#        self.assertEqual(_split_selector('A, B'), [['A'], ['B']])
#        self.assertEqual(_split_selector('A, B, C'), [['A'], ['B'], ['C']])
#
#    def test_alt_spaces(self):
#        self.assertEqual(_split_selector('A,B'), [['A'], ['B']])
#        self.assertEqual(_split_selector('A, B'), [['A'], ['B']])
#        self.assertEqual(_split_selector('A ,B'), [['A'], ['B']])
#        self.assertEqual(_split_selector('A , B'), [['A'], ['B']])
#
#    def test_descr(self):
#        self.assertEqual(_split_selector('A'), [['A']])
#        self.assertEqual(_split_selector('A B'), [['A', 'B']])
#        self.assertEqual(_split_selector('A B C'), [['A', 'B', 'C']])
#
#    def test_pure_group(self):
#        def opt(res):
#            return (res, [[res]])
#        self.assertIn(_split_selector('{A}'), opt([['A']]))
#        self.assertIn(_split_selector('{A, B}'), opt([['A'], ['B']]))
#
#    def test_desc_group(self):
#        self.assertEqual(_split_selector('A {B, C}'), [['A', [['B'], ['C']]]])
#        self.assertEqual(_split_selector('A {B, C} D'), [['A', [['B'], ['C']], 'D']])

