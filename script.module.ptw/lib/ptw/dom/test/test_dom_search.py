# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

from .base import TestCase
from unittest import skip as skiptest, skipIf as skiptestIf

from ..msearch import dom_search
from ..base import aWord, aWordStarts, aStarts, aEnds, aContains
from ..base import DomMatch, ResultParam, MissingAttr   # for test only






class TestDomSearch(TestCase):

    def test_input(self):
        with self.subTest('Unicode      (Py2: unicode, Py3: str)'):
            self.assertEqual(dom_search('<a>A</a>', 'a'), ['A'])
        with self.subTest('Bytes        (Py2: str,     Py3: bytes)'):
            self.assertEqual(dom_search(b'<a>A</a>', 'a'), ['A'])
        with self.subTest('Unicode list (Py2: unicode, Py3: str)'):
            self.assertEqual(dom_search(['<a>A</a>'], 'a'), ['A'])
            self.assertEqual(dom_search(['<a>A</a>', '<a>A</a>'], 'a'), ['A', 'A'])
        with self.subTest('Bytes list   (Py2: str,     Py3: bytes)'):
            self.assertEqual(dom_search([b'<a>A</a>'], 'a'), ['A'])
            self.assertEqual(dom_search([b'<a>A</a>', b'<a>A</a>'], 'a'), ['A', 'A'])
        with self.subTest('Mixed list   (Py2: unicode + str,  Py3: str + bytes)'):
            self.assertEqual(dom_search(['<a>A</a>', b'<a>A</a>'], 'a'), ['A', 'A'])

    def test_tag(self):
        with self.subTest('A'):
            self.assertEqual(dom_search('<a>A</a>', 'a'), ['A'])
        with self.subTest('A, A'):
            self.assertEqual(dom_search('<a>A</a><a>B</a>', 'a'), ['A', 'B'])
        with self.subTest('A, X'):
            self.assertEqual(dom_search('<a>A</a><x>X</x>', 'a'), ['A'])
        with self.subTest('X, A'):
            self.assertEqual(dom_search('<x>X</x><a>A</a>', 'a'), ['A'])
        with self.subTest('X > A'):
            self.assertEqual(dom_search('<x><a>A</a></x>', 'a'), ['A'])
        with self.subTest('A > X'):
            self.assertEqual(dom_search('<a><x>A</x></a>', 'a'), ['<x>A</x>'])

    #@skiptest('Not fixed yet')
    def test_tag_nested(self):
        with self.subTest('A > A'):
            self.assertEqual(dom_search('<a>A<a>B</a></a>', 'a'), ['A<a>B</a>', 'B'])
        with self.subTest('A > A ...'):
            self.assertEqual(dom_search('<a>A<a>B</a>C</a>Q', 'a'), ['A<a>B</a>C', 'B'])
            self.assertEqual(dom_search('<a>A<a></a>C</a>Q', 'a'), ['A<a></a>C', ''])
            self.assertEqual(dom_search('<a><a>B</a>C</a>Q', 'a'), ['<a>B</a>C', 'B'])
            self.assertEqual(dom_search('<a>A<a>B</a></a>Q', 'a'), ['A<a>B</a>', 'B'])
            self.assertEqual(dom_search('<a><a>B</a></a>Q', 'a'), ['<a>B</a>', 'B'])
            self.assertEqual(dom_search('<a><a></a></a>Q', 'a'), ['<a></a>', ''])
        with self.subTest('A > A > A'):
            self.assertEqual(dom_search('<a>A<a>B<a>C</a></a></a>', 'a'), ['A<a>B<a>C</a></a>', 'B<a>C</a>', 'C'])
        with self.subTest('A, A > A'):
            self.assertEqual(dom_search('<a>C</a><a>A<a>B</a></a>', 'a'), ['C', 'A<a>B</a>', 'B'])
        with self.subTest('A > A, A'):
            self.assertEqual(dom_search('<a>A<a>B</a></a><a>C</a>', 'a'), ['A<a>B</a>', 'B', 'C'])
        with self.subTest('A > A, A > A'):
            self.assertEqual(dom_search('<a>A<a>B</a></a><a>C<a>D</a></a>', 'a'), ['A<a>B</a>', 'B', 'C<a>D</a>', 'D'])
        with self.subTest('A > X > A ...'):
            self.assertEqual(dom_search('<a>A<x>B<a>C</a>D</x>E</a>Q', 'a'), ['A<x>B<a>C</a>D</x>E', 'C'])

    def test_tag_single(self):
        with self.subTest('A/'):
            self.assertEqual(dom_search('<a/>', 'a'), [''])
        with self.subTest('A /'):
            self.assertEqual(dom_search('<a />', 'a'), [''])
        with self.subTest('X > A/, A'):
            self.assertEqual(dom_search('<x><a/></x><a>A</a>', 'a'), ['', 'A'])
        with self.subTest('X > A /, A'):
            self.assertEqual(dom_search('<x><a /></x><a>A</a>', 'a'), ['', 'A'])
        with self.subTest('X > A/, A ...'):
            self.assertEqual(dom_search('<x><a/></x><a>A</a>Q', 'a'), ['', 'A'])
        with self.subTest('X > A /, A ...'):
            self.assertEqual(dom_search('<x><a /></x><a>A</a>Q', 'a'), ['', 'A'])
        with self.subTest('X > ( A/, A )'):
            self.assertEqual(dom_search('<x><a/><a>A</a></x>', 'a'), ['', 'A'])
        with self.subTest('X > ( A /, A )'):
            self.assertEqual(dom_search('<x><a /></x><a>A</a></x>', 'a'), ['', 'A'])
        with self.subTest('X > ( A/, A ) ...'):
            self.assertEqual(dom_search('<x><a/><a>A</a></x>Q', 'a'), ['', 'A'])
        with self.subTest('X > ( A /, A ) ...'):
            self.assertEqual(dom_search('<x><a /><a>A</a></x>Q', 'a'), ['', 'A'])
        with self.subTest('X > ( A /, A ... )'):
            self.assertEqual(dom_search('<x><a /><a>A</a>Q</x>', 'a'), ['', 'A'])
        with self.subTest('X > ( A/, A ... )'):
            self.assertEqual(dom_search('<x><a/><a>A</a>Q</x>', 'a'), ['', 'A'])

    def test_tag_nested_single(self):
        with self.subTest('A > A/'):
            self.assertEqual(dom_search('<a>A<a/>B</a>', 'a'), ['A<a/>B', ''])
            self.assertEqual(dom_search('<a>A<a/></a>', 'a'), ['A<a/>', ''])
            self.assertEqual(dom_search('<a><a/>B</a>', 'a'), ['<a/>B', ''])
            self.assertEqual(dom_search('<a><a/></a>', 'a'), ['<a/>', ''])
        with self.subTest('A > A /'):
            self.assertEqual(dom_search('<a>A<a />B</a>', 'a'), ['A<a />B', ''])
            self.assertEqual(dom_search('<a>A<a /></a>', 'a'), ['A<a />', ''])
            self.assertEqual(dom_search('<a><a />B</a>', 'a'), ['<a />B', ''])
            self.assertEqual(dom_search('<a><a /></a>', 'a'), ['<a />', ''])
        with self.subTest('A > A/ ...'):
            self.assertEqual(dom_search('<a>A<a/>B</a>Q', 'a'), ['A<a/>B', ''])
        with self.subTest('A > A / ...'):
            self.assertEqual(dom_search('<a>A<a />B</a>Q', 'a'), ['A<a />B', ''])
        with self.subTest('A > A/ ... /a'):
            self.assertEqual(dom_search('<a>A<a/>B</a>Q</a>', 'a'), ['A<a/>B', ''])
        with self.subTest('A > A / ... /a'):
            self.assertEqual(dom_search('<a>A<a />B</a>Q</a>', 'a'), ['A<a />B', ''])
        with self.subTest('A > X > A/ ...'):
            self.assertEqual(dom_search('<a>A<x>B<a/>C</x>D</a>Q', 'a'), ['A<x>B<a/>C</x>D', ''])
        with self.subTest('A > X > A / ...'):
            self.assertEqual(dom_search('<a>A<x>B<a />C</x>D</a>Q', 'a'), ['A<x>B<a />C</x>D', ''])
        with self.subTest('A > X > A/ ... /a'):
            self.assertEqual(dom_search('<a>A<x>B<a/>C</x>D</a>Q</a>', 'a'), ['A<x>B<a/>C</x>D', ''])
        with self.subTest('A > X > A / ... /a'):
            self.assertEqual(dom_search('<a>A<x>B<a />C</x>D</a>Q</a>', 'a'), ['A<x>B<a />C</x>D', ''])

    def test_tag_broken_nested(self):
        with self.subTest('A > X > ~A~ ...'):
            self.assertEqual(dom_search('<a>A<x>B<a>C</x>D</a>Q', 'a'), ['A<x>B<a>C</x>D', 'C'])
        with self.subTest('A > X > ~A~ ... /a'):
            self.assertEqual(dom_search('<a>A<x>B<a>C</x>D</a>Q</a>', 'a'), ['A<x>B<a>C</x>D', 'C'])
        with self.subTest('A > X > ( ~A~, ~A~ ) ... /a'):
            self.assertEqual(dom_search('<a>A<x>B<a>C<a>D</x>E</a>Q</a>', 'a'), ['A<x>B<a>C<a>D</x>E', 'C<a>D', 'D'])
        with self.subTest('A > ( X > ~A~, X > ~A~ ) ... /a'):
            self.assertEqual(dom_search('<a>A<x>B<a>C</x>D<x>E<a>F</x>G</a>Q</a>', 'a'), ['A<x>B<a>C</x>D<x>E<a>F</x>G', 'C', 'F'])

    def test_tag_broken_nested_single(self):
        '<a>z<x>x<a>aa</a>y</x></a>',
        '<a>z<x>x<a>y</x></a>Q</a>',

    def test_no_attrs(self):
        self.assertEqual(dom_search('<a x="1">A</a>', 'a'), ['A'])
        self.assertEqual(dom_search('<a>A</a><a x="1">B</a>', 'a'), ['A', 'B'])

    def test_1_attrs(self):
        self.assertEqual(dom_search('<a>A</a>', 'a', {'x': '1'}), [])
        self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': '1'}), ['A'])
        self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': '1'}), [])
        self.assertEqual(dom_search('<a y="1">A</a>', 'a', {'x': '1'}), [])
        self.assertEqual(dom_search('<a>A</a><a x="1">B</a>', 'a', {'x': '1'}), ['B'])
        self.assertEqual(dom_search('<a x="1">A</a><a>B</a>', 'a', {'x': '1'}), ['A'])
        self.assertEqual(dom_search('<a x="1">A<a>B</a></a>', 'a', {'x': '1'}), ['A<a>B</a>'])

    def test_2_attrs(self):
        self.assertEqual(dom_search('<a>A</a>', 'a', {'x': '1', 'y': '2'}), [])
        self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': '1', 'y': '2'}), [])
        self.assertEqual(dom_search('<a y="2">A</a>', 'a', {'x': '1', 'y': '2'}), [])
        self.assertEqual(dom_search('<a x="2" y="2">A</a>', 'a', {'x': '1', 'y': '2'}), [])
        self.assertEqual(dom_search('<a x="1" y="3">A</a>', 'a', {'x': '1', 'y': '2'}), [])
        self.assertEqual(dom_search('<a x="1" y="2">A</a>', 'a', {'x': '1', 'y': '2'}), ['A'])
        self.assertEqual(dom_search('<a>A</a><a x="1" y="2">B</a>', 'a', {'x': '1', 'y': '2'}), ['B'])
        self.assertEqual(dom_search('<a x="1">A</a><a x="1" y="2">B</a>', 'a', {'x': '1', 'y': '2'}), ['B'])
        self.assertEqual(dom_search('<a y="2">A</a><a x="1" y="2">B</a>', 'a', {'x': '1', 'y': '2'}), ['B'])
        self.assertEqual(dom_search('<a x="1" y="2">A</a><a x="1" y="2">B</a>', 'a', {'x': '1', 'y': '2'}), ['A', 'B'])
        self.assertEqual(dom_search('<a x="1" y="2"><a>A</a></a>', 'a', {'x': '1', 'y': '2'}), ['<a>A</a>'])

    def test_all_tags(self):
        with self.subTest('Any tag'):
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', None), ['A', 'B', 'C'])
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', False), ['A', 'B', 'C'])
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', ''), ['A', 'B', 'C'])
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', b''), ['A', 'B', 'C'])
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', '*'), ['A', 'B', 'C'])
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', b'*'), ['A', 'B', 'C'])
        with self.subTest('*'):
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', '*'), ['A', 'B', 'C'])
            self.assertEqual(dom_search('<a x="1">A</a><b x="1">B</b><c>C</c>', None), ['A', 'B', 'C'])

    def test_only_attrs(self):
        with self.subTest('*[x]'):
            self.assertEqual(dom_search('<a>A</a><b>B</b><c>C</c>', '*', {'x': '1'}), [])
            self.assertEqual(dom_search('<a x="1">A</a><b x="1">B</b><c>C</c>', '', {'x': '1'}), ['A', 'B'])
            self.assertEqual(dom_search('<a x="1">A</a><b x="1">B</b><c>C</c>', '*', {'x': '1'}), ['A', 'B'])

    def test_content(self):
        with self.subTest('A'):
            self.assertEqual(dom_search('<a>A</a>', 'a'), ['A'])
            self.assertEqual(dom_search('<a>A</a>Q', 'a'), ['A'])
            self.assertEqual(dom_search('Q<a>A</a>', 'a'), ['A'])
            self.assertEqual(dom_search('Q<a>A</a>Q', 'a'), ['A'])
        with self.subTest('Omit ">" in attr'):
            self.assertEqual(dom_search('<a z=">">A</a>Q', 'a'), ['A'])

    def test_ret_attr(self):
        with self.subTest('A {content}'):
            self.assertEqual(dom_search('<a>A</a>', 'a', ret=False), ['A'])
        with self.subTest('A[x] {content}'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', ret=False), ['A'])
        with self.subTest('A {attr}'):
            self.assertEqual(dom_search('<a>A</a>', 'a', ret='x'), [])
        with self.subTest('A[x] {attr}'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', ret='x'), ['1'])

    def test_many_parts(self):
        with self.subTest('Parts: A'):
            self.assertEqual(dom_search(['<a>A</a>', '<a>A</a>'], 'a'), ['A', 'A'])
        with self.subTest('Parts: A, A'):
            self.assertEqual(dom_search(['<a>A</a><a>B</a>', '<a>A</a><a>B</a>'], 'a'), ['A', 'B', 'A', 'B'])
        with self.subTest('Parts: [A, B], [B A]'):
            self.assertEqual(dom_search(['<a>A</a><b>B</b>', '<b>A</b><a>B</a>'], 'a'), ['A', 'B'])
        with self.subTest('Parts: A, B'):
            self.assertEqual(dom_search(['<a>A</a><b>B</b>', '<a>A</a><b>B</b>'], 'a'), ['A', 'A'])
        with self.subTest('Parts: A > A'):
            self.assertEqual(dom_search(['<a>A<a>B</a>C</a>', '<a>A<a>B</a>C</a>'], 'a'), ['A<a>B</a>C', 'B', 'A<a>B</a>C', 'B'])

    def test_many_parts_attr(self):
        with self.subTest('Parts: A[x], A'):
            self.assertEqual(dom_search(['<a x="1">A</a><a>B</a>', '<a x="1">A</a><a>B</a>'], 'a', {'x': '1'}), ['A', 'A'])

    def test_many_parts_ret(self):
        with self.subTest('Parts: A, A {attr}'):
            self.assertEqual(dom_search(['<a x="1">A</a><a>B</a>', '<a x="1">A</a><a>B</a>'], 'a', {}, ret='x'), ['1', '1'])
        with self.subTest('Parts: A[x], A {attr}'):
            self.assertEqual(dom_search(['<a x="1">A</a><a>B</a>', '<a x="1">A</a><a>B</a>'], 'a', {'x': '1'}, ret='x'), ['1', '1'])

    def test_case_sensitive_tag(self):
        with self.subTest('Case sensitive: search a in a'):
            self.assertEqual(dom_search('<a>A</a>', 'a'), ['A'])
        with self.subTest('Case sensitive: search A in a'):
            self.assertEqual(dom_search('<a>A</a>', 'A'), ['A'])
        with self.subTest('Case sensitive: search a in A'):
            self.assertEqual(dom_search('<A>A</A>', 'a'), ['A'])
        with self.subTest('Case sensitive: search A in A'):
            self.assertEqual(dom_search('<A>A</A>', 'A'), ['A'])

    def test_case_sensitive_attr(self):
        with self.subTest('Case sensitive: search x in x'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': True}), ['A'])
        with self.subTest('Case sensitive: search X in x'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': True}), ['A'])
        with self.subTest('Case sensitive: search x in X'):
            self.assertEqual(dom_search('<a X="1">A</a>', 'a', {'x': True}), ['A'])
        with self.subTest('Case sensitive: search X in X'):
            self.assertEqual(dom_search('<a X="1">A</a>', 'a', {'x': True}), ['A'])



class TestDomSearch_Extra(TestCase):

    def test_attr_bool(self):
        with self.subTest('A[x=True]'):
            self.assertEqual(dom_search('<a>A</a>', 'a', {'x': True}), [])
            self.assertEqual(dom_search('<a x>A</a>', 'a', {'x': True}), ['A'])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': True}), ['A'])
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': True}), ['A'])
            self.assertEqual(dom_search('<a y>A</a>', 'a', {'x': True}), [])
            self.assertEqual(dom_search('<a y="">A</a>', 'a', {'x': True}), [])
            self.assertEqual(dom_search('<a y="1">A</a>', 'a', {'x': True}), [])
        with self.subTest('A[x=False]'):
            self.assertEqual(dom_search('<a>A</a>', 'a', {'x': False}), ['A'])
            self.assertEqual(dom_search('<a x>A</a>', 'a', {'x': False}), [])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': False}), [])
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': False}), [])
            self.assertEqual(dom_search('<a x="1" y="2">A</a>', 'a', {'x': False}), [])
            self.assertEqual(dom_search('<a y="2" x="1">A</a>', 'a', {'x': False}), [])
            self.assertEqual(dom_search('<a y="1">A</a>', 'a', {'x': False}), ['A'])
        with self.subTest('A[x=None]'):
            self.assertEqual(dom_search('<a x>A</a>', 'a', {'x': None}), ['A'])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': None}), ['A'])
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': None}), ['A'])
            self.assertEqual(dom_search('<a y>A</a>', 'a', {'x': None}), ['A'])
            self.assertEqual(dom_search('<a y="">A</a>', 'a', {'x': None}), ['A'])
            self.assertEqual(dom_search('<a y="1">A</a>', 'a', {'x': None}), ['A'])

    def test_attr_empty(self):
        # atribbute value [] match any attrbuite value (attribute must exist)
        with self.subTest('A[x=[]]'):
            self.assertEqual(dom_search('<a x>A</a>', 'a', {'x': []}), ['A'])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': []}), ['A'])
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': []}), ['A'])
            self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': []}), ['A'])
            self.assertEqual(dom_search('<a x="1 2">A</a>', 'a', {'x': []}), ['A'])
        with self.subTest('A[x=[]] - no attr'):
            self.assertEqual(dom_search('<a>A</a>', 'a', {'x': []}), [])
        with self.subTest('A[x=[]] - wrong attr'):
            self.assertEqual(dom_search('<a>A</a>', 'a', {'x': []}), [])
            self.assertEqual(dom_search('<a y="">A</a>', 'a', {'x': []}), [])
            self.assertEqual(dom_search('<a y="1">A</a>', 'a', {'x': []}), [])
        with self.subTest('A[x=[]] - wrong tag'):
            self.assertEqual(dom_search('<b x="">A</b>', 'a', {'x': []}), [])
            self.assertEqual(dom_search('<b y="">A</b>', 'a', {'x': []}), [])

    def test_attr_or(self):
        with self.subTest('A[x=1|2]'):
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': '1|2'}), [])
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': '1|2'}), ['A'])
            self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': '1|2'}), ['A'])
            self.assertEqual(dom_search('<a x="3">A</a>', 'a', {'x': '1|2'}), [])
        with self.subTest('A[x=1|2][y]'):
            self.assertEqual(dom_search('<a x="1" y="5">A</a>', 'a', {'x': '1|2', 'y': '5'}), ['A'])
            self.assertEqual(dom_search('<a x="2" y="5">A</a>', 'a', {'x': '1|2', 'y': '5'}), ['A'])
            self.assertEqual(dom_search('<a x="3" y="5">A</a>', 'a', {'x': '1|2', 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="1" y="6">A</a>', 'a', {'x': '1|2', 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="2" y="6">A</a>', 'a', {'x': '1|2', 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="3" y="6">A</a>', 'a', {'x': '1|2', 'y': '5'}), [])

    def test_attr_list_and(self):
        with self.subTest(r'A[x[\b1,2\b]]'):
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b']}), ['A'])
            self.assertEqual(dom_search('<a x="21">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b']}), [])
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b']}), [])
            self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b']}), [])
            self.assertEqual(dom_search('<a x="3">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b']}), [])
        with self.subTest(r'A[x[\b1,2\b]][y] (y matchs)'):
            self.assertEqual(dom_search('<a x="12" y="5">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), ['A'])
            self.assertEqual(dom_search('<a x="21" y="5">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="1" y="5">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="2" y="5">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="3" y="5">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
        with self.subTest(r'A[x[\b1,2\b]][y] (y does not match)'):
            self.assertEqual(dom_search('<a x="12" y="6">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="21" y="6">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="1" y="6">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="2" y="6">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])
            self.assertEqual(dom_search('<a x="3" y="6">A</a>', 'a', {'x': [r'\b1.*?', r'.*?2\b'], 'y': '5'}), [])

    def test_comments(self):
        with self.subTest('Exclude comments: no comments'):
            self.assertEqual(dom_search('<a>A</a>', 'a'), ['A'])
        with self.subTest('Exclude comments: one comment'):
            self.assertEqual(dom_search('<a>A<!-- X --></a>', 'a'), ['A<!-- X -->'])
            #self.assertEqual(dom_search('<a>A<!-- X --></a>', 'a', exclude_comments=True), ['A'])
            #self.assertEqual(dom_search('<a><!-- X -->A</a>', 'a', exclude_comments=True), ['A'])



class TestDomSearch_AttrFunc(TestCase):

    def test_attr_func_aWord_1(self):
        with self.subTest('One aWord() – empty'):
            self.assertEqual(dom_search('<a x=>A</a>', 'a', {'x': aWord('1')}), [])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': aWord('1')}), [])
        with self.subTest('One aWord() - single value'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': aWord('1')}), ['A'])
            self.assertEqual(dom_search('<a x=" 1">A</a>', 'a', {'x': aWord('1')}), ['A'])
            self.assertEqual(dom_search('<a x="1 ">A</a>', 'a', {'x': aWord('1')}), ['A'])
            self.assertEqual(dom_search('<a x="11">A</a>', 'a', {'x': aWord('1')}), [])
        with self.subTest('One aWord() - many values'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': aWord('1')}), ['A'])
            self.assertEqual(dom_search('<a x="1 2">A</a>', 'a', {'x': aWord('1')}), ['A'])
            self.assertEqual(dom_search('<a x="2 1">A</a>', 'a', {'x': aWord('1')}), ['A'])
            self.assertEqual(dom_search('<a x="2 1 3">A</a>', 'a', {'x': aWord('1')}), ['A'])
        with self.subTest('One aWord() - miss'):
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': aWord('1')}), [])
            self.assertEqual(dom_search('<a x="2 11 3">A</a>', 'a', {'x': aWord('1')}), [])
            self.assertEqual(dom_search('<a x="2 3">A</a>', 'a', {'x': aWord('1')}), [])

    def test_attr_func_aWord_2(self):
        with self.subTest('Two aWord() - miss, no one exists'):
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
            self.assertEqual(dom_search('<a x="3">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
            self.assertEqual(dom_search('<a y="1 2">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
            self.assertEqual(dom_search('<a y="11 22">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
        with self.subTest('Two aWord() - miss, one exists'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
            self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
            self.assertEqual(dom_search('<a x="1 22">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
            self.assertEqual(dom_search('<a x="11 2">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), [])
        with self.subTest('Two aWord() - two exist'):
            self.assertEqual(dom_search('<a x="1 2">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="2 1">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="1 2 3">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="0 1 2">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="0 1 2 3">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="0 2 1 3">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="1 0 2">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="2 0 1">A</a>', 'a', {'x': [ aWord('1'), aWord('2') ] }), ['A'])

    def test_attr_func_aWordStarts_1(self):
        with self.subTest('One aWordStart() – empty'):
            self.assertEqual(dom_search('<a x=>A</a>', 'a', {'x': aWordStarts('1')}), [])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': aWordStarts('1')}), [])
        with self.subTest('One aWordStart() – single value'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x=" 1">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="1 ">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="11">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="21">A</a>', 'a', {'x': aWordStarts('1')}), [])
        with self.subTest('One aWordStart() – many values'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="1 2">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="2 1">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="2 1 3">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="2 11 3">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="2 12 3">A</a>', 'a', {'x': aWordStarts('1')}), ['A'])
        with self.subTest('One aWordStart() - miss'):
            self.assertEqual(dom_search('<a x="21">A</a>', 'a', {'x': aWordStarts('1')}), [])
            self.assertEqual(dom_search('<a x="2 21 3">A</a>', 'a', {'x': aWordStarts('1')}), [])
            self.assertEqual(dom_search('<a x="2 3">A</a>', 'a', {'x': aWordStarts('1')}), [])

    def test_attr_func_aWordStarts_2(self):
        with self.subTest('Two aWordStarts() - miss, no one exists'):
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="3">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a y="1 2">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a y="11 22">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="21">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
        with self.subTest('Two aWordStarts() - miss, one exists'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="1 12">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="21 2">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="3 12">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
            self.assertEqual(dom_search('<a x="21 3">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), [])
        with self.subTest('Two aWordStarts() - two exist'):
            self.assertEqual(dom_search('<a x="1 2">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="2 1">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="1 2 3">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="0 1 2">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="0 1 2 3">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="0 2 1 3">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="1 0 2">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="2 0 1">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="1 22">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="11 2">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="12 21">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])
            self.assertEqual(dom_search('<a x="12 33 21">A</a>', 'a', {'x': [ aWordStarts('1'), aWordStarts('2') ] }), ['A'])

    def test_attr_func_aStarts(self):
        with self.subTest('One aStarts() – empty'):
            self.assertEqual(dom_search('<a x=>A</a>', 'a', {'x': aStarts('1')}), [])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': aStarts('1')}), [])
            self.assertEqual(dom_search('<a x=" ">A</a>', 'a', {'x': aStarts('1')}), [])
        with self.subTest('One aStarts() – miss'):
            self.assertEqual(dom_search('<a x=" 1">A</a>', 'a', {'x': aStarts('1')}), [])
            self.assertEqual(dom_search('<a x=" 1 1">A</a>', 'a', {'x': aStarts('1')}), [])
            self.assertEqual(dom_search('<a x="3 1">A</a>', 'a', {'x': aStarts('1')}), [])
            self.assertEqual(dom_search('<a x="31">A</a>', 'a', {'x': aStarts('1')}), [])
        with self.subTest('One aStarts() – match'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': aStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="1 1">A</a>', 'a', {'x': aStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="11">A</a>', 'a', {'x': aStarts('1')}), ['A'])
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': aStarts('1')}), ['A'])
        with self.subTest('One aStarts() – miss, two cond on "x"'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': [aStarts('1'), aStarts('2')]}), [])
            self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': [aStarts('1'), aStarts('2')]}), [])
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': [aStarts('1'), aStarts('2')]}), [])
            self.assertEqual(dom_search('<a x="21">A</a>', 'a', {'x': [aStarts('1'), aStarts('2')]}), [])
        with self.subTest('One aStarts() – match (x, y)'):
            self.assertEqual(dom_search('<a x="1" y="2">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), ['A'])
            self.assertEqual(dom_search('<a x="11" y="2">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), ['A'])
            self.assertEqual(dom_search('<a x="1" y="22">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), ['A'])
            self.assertEqual(dom_search('<a x="1 2" y="2 1">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), ['A'])
        with self.subTest('One aStarts() – miss (x, y)'):
            self.assertEqual(dom_search('<a x="1" y="3">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), [])
            self.assertEqual(dom_search('<a x="3" y="2">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), [])
            self.assertEqual(dom_search('<a x="21" y="2">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), [])
            self.assertEqual(dom_search('<a x="1" y="32">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), [])
            self.assertEqual(dom_search('<a x="2 1" y="1 2">A</a>', 'a', {'x': aStarts('1'), 'y': aStarts('2')}), [])

    def test_attr_func_aEnds(self):
        with self.subTest('One aEnds() – empty'):
            self.assertEqual(dom_search('<a x=>A</a>', 'a', {'x': aEnds('1')}), [])
            self.assertEqual(dom_search('<a x="">A</a>', 'a', {'x': aEnds('1')}), [])
            self.assertEqual(dom_search('<a x=" ">A</a>', 'a', {'x': aEnds('1')}), [])
        with self.subTest('One aEnds() – miss'):
            self.assertEqual(dom_search('<a x="1 ">A</a>', 'a', {'x': aEnds('1')}), [])
            self.assertEqual(dom_search('<a x="1 1 ">A</a>', 'a', {'x': aEnds('1')}), [])
            self.assertEqual(dom_search('<a x="1 3">A</a>', 'a', {'x': aEnds('1')}), [])
            self.assertEqual(dom_search('<a x="13">A</a>', 'a', {'x': aEnds('1')}), [])
        with self.subTest('One aEnds() – match'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': aEnds('1')}), ['A'])
            self.assertEqual(dom_search('<a x="1 1">A</a>', 'a', {'x': aEnds('1')}), ['A'])
            self.assertEqual(dom_search('<a x="11">A</a>', 'a', {'x': aEnds('1')}), ['A'])
            self.assertEqual(dom_search('<a x="21">A</a>', 'a', {'x': aEnds('1')}), ['A'])
        with self.subTest('One aEnds() – miss, two cond on "x"'):
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', {'x': [aEnds('1'), aEnds('2')]}), [])
            self.assertEqual(dom_search('<a x="2">A</a>', 'a', {'x': [aEnds('1'), aEnds('2')]}), [])
            self.assertEqual(dom_search('<a x="12">A</a>', 'a', {'x': [aEnds('1'), aEnds('2')]}), [])
            self.assertEqual(dom_search('<a x="21">A</a>', 'a', {'x': [aEnds('1'), aEnds('2')]}), [])
        with self.subTest('One aEnds() – match (x, y)'):
            self.assertEqual(dom_search('<a x="1" y="2">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), ['A'])
            self.assertEqual(dom_search('<a x="11" y="2">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), ['A'])
            self.assertEqual(dom_search('<a x="1" y="22">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), ['A'])
            self.assertEqual(dom_search('<a x="2 1" y="1 2">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), ['A'])
        with self.subTest('One aEnds() – miss (x, y)'):
            self.assertEqual(dom_search('<a x="1" y="3">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), [])
            self.assertEqual(dom_search('<a x="3" y="2">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), [])
            self.assertEqual(dom_search('<a x="12" y="2">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), [])
            self.assertEqual(dom_search('<a x="1" y="23">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), [])
            self.assertEqual(dom_search('<a x="1 2" y="2 1">A</a>', 'a', {'x': aEnds('1'), 'y': aEnds('2')}), [])



class TestDomSearch_DomMatch(TestCase):
    # DomMach result, almost compatibile with Cherry dom_parse()

    def test_dommatch_base(self):
        with self.subTest('DomMatch ret'):
            self.assertEqual(dom_search('<b>B</b>', 'a', ret=DomMatch), [])
            self.assertEqual(len(dom_search('<a>A</a>', 'a', ret=DomMatch)), 1)
        with self.subTest('DomMatch type'):
            self.assertEqual(dom_search('<a>A</a>', 'a', ret=DomMatch), [DomMatch({}, 'A')])
            self.assertEqual(type(dom_search('<a>A</a>', 'a', ret=DomMatch)[0]), DomMatch)

    def test_dommatch_content(self):
        with self.subTest('DomMatch content by name'):
            self.assertEqual(dom_search('<a>A</a>', 'a', ret=DomMatch)[0].content, 'A')
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', ret=DomMatch)[0].content, 'A')
        with self.subTest('DomMatch content by index'):
            self.assertEqual(dom_search('<a>A</a>', 'a', ret=DomMatch)[0][1], 'A')
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', ret=DomMatch)[0][1], 'A')

    def test_dommatch_attr(self):
        with self.subTest('DomMatch attr by name'):
            self.assertEqual(dom_search('<a>A</a>', 'a', ret=DomMatch)[0].attrs, {})
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', ret=DomMatch)[0].attrs, {'x': '1'})
        with self.subTest('DomMatch attr by index'):
            self.assertEqual(dom_search('<a>A</a>', 'a', ret=DomMatch)[0][0], {})
            self.assertEqual(dom_search('<a x="1">A</a>', 'a', ret=DomMatch)[0][0], {'x': '1'})
        with self.subTest('DomMatch many attrs'):
            self.assertEqual(dom_search('<a x="1" y="2">A</a>', 'a', ret=DomMatch)[0].attrs, {'x': '1', 'y': '2'})
            self.assertEqual(dom_search('<a y="2" x="1">A</a>', 'a', ret=DomMatch)[0].attrs, {'x': '1', 'y': '2'})

    def test_dommatch_source_list(self):
        sA, sAA = '<a>A</a>', '<a>A</a><a>A</a>'
        sAx, sAAx, sAxAx = '<a x="1">A</a>', '<a>A</a><a x="1">A</a>', '<a x="1">A</a><a x="1">A</a>'
        mA, mAA = DomMatch({}, sA), DomMatch({}, sAA)
        mAx, mAAx, mAxAx = DomMatch({}, sAx), DomMatch({}, sAAx), DomMatch({}, sAxAx)
        A, Ax = DomMatch({}, 'A'), DomMatch({'x': '1'}, 'A')
        with self.subTest('Source list -> DomMatch'):
            self.assertEqual(dom_search([sA], 'a', ret=DomMatch), [A])
            self.assertEqual(dom_search([sAA], 'a', ret=DomMatch), [A, A])
            self.assertEqual(dom_search([sA, sA], 'a', ret=DomMatch), [A, A])
        with self.subTest('Source list (attr) -> DomMatch'):
            self.assertEqual(dom_search([sAx], 'a', ret=DomMatch), [Ax])
            self.assertEqual(dom_search([sAxAx], 'a', ret=DomMatch), [Ax, Ax])
            self.assertEqual(dom_search([sAAx], 'a', ret=DomMatch), [A, Ax])
            self.assertEqual(dom_search([sAx, sAx], 'a', ret=DomMatch), [Ax, Ax])

    def test_dommatch_source_dommatch_list(self):
        sA, sAA = '<a>A</a>', '<a>A</a><a>A</a>'
        sAx, sAAx, sAxAx = '<a x="1">A</a>', '<a>A</a><a x="1">A</a>', '<a x="1">A</a><a x="1">A</a>'
        mA, mAA = DomMatch({}, sA), DomMatch({}, sAA)
        mAx, mAAx, mAxAx = DomMatch({}, sAx), DomMatch({}, sAAx), DomMatch({}, sAxAx)
        A, Ax = DomMatch({}, 'A'), DomMatch({'x': '1'}, 'A')
        with self.subTest('Source DomMatch list -> DomMatch'):
            self.assertEqual(dom_search([sA], 'a', ret=DomMatch), [A])
            self.assertEqual(dom_search([sAA], 'a', ret=DomMatch), [A, A])
            self.assertEqual(dom_search([sA, sA], 'a', ret=DomMatch), [A, A])
        with self.subTest('Source DomMatch list (attr) -> DomMatch'):
            self.assertEqual(dom_search([mAx], 'a', ret=DomMatch), [Ax])
            self.assertEqual(dom_search([mAxAx], 'a', ret=DomMatch), [Ax, Ax])
            self.assertEqual(dom_search([mAAx], 'a', ret=DomMatch), [A, Ax])
            self.assertEqual(dom_search([mAx, mAx], 'a', ret=DomMatch), [Ax, Ax])

    def test_dommatch_source_mixed_list(self):
        sA, sAA = '<a>A</a>', '<a>A</a><a>A</a>'
        sAx, sAAx, sAxAx = '<a x="1">A</a>', '<a>A</a><a x="1">A</a>', '<a x="1">A</a><a x="1">A</a>'
        mA, mAA = DomMatch({}, sA), DomMatch({}, sAA)
        mAx, mAAx, mAxAx = DomMatch({}, sAx), DomMatch({}, sAAx), DomMatch({}, sAxAx)
        A, Ax = DomMatch({}, 'A'), DomMatch({'x': '1'}, 'A')
        with self.subTest('Source mixed list -> DomMatch'):
            self.assertEqual(dom_search([sA, mA], 'a', ret=DomMatch), [A, A])
            self.assertEqual(dom_search([mA, sA], 'a', ret=DomMatch), [A, A])
        with self.subTest('Source mixed list (attr) -> DomMatch'):
            self.assertEqual(dom_search([mAx], 'a', ret=DomMatch), [Ax])
            self.assertEqual(dom_search([mAxAx], 'a', ret=DomMatch), [Ax, Ax])
            self.assertEqual(dom_search([mAAx], 'a', ret=DomMatch), [A, Ax])
            self.assertEqual(dom_search([mAx, mAx], 'a', ret=DomMatch), [Ax, Ax])

    def test_tuple(self):
        sA = '<a>A</a>'
        mA = DomMatch({}, sA)
        with self.subTest('MatchDom vs. tuple'):
            self.assertEqual(dom_search(mA, 'a'), ['A'])
            self.assertEqual(dom_search([mA], 'a'), ['A'])
            self.assertEqual(dom_search((mA,), 'a'), ['A'])
        mA = DomMatch({'x': '1'}, sA)
        with self.subTest('MatchDom(attrs) vs. tuple'):
            self.assertEqual(dom_search(mA, 'a'), ['A'])
            self.assertEqual(dom_search([mA], 'a'), ['A'])
            self.assertEqual(dom_search((mA,), 'a'), ['A'])
        mA = DomMatch({'<a>X</a>': '1'}, sA)
        with self.subTest('MatchDom(fake attrs) vs. tuple'):
            self.assertEqual(dom_search(mA, 'a'), ['A'])
            self.assertEqual(dom_search([mA], 'a'), ['A'])
            self.assertEqual(dom_search((mA,), 'a'), ['A'])


class TestDomSearch_ResultParam(TestCase):

    def test_missing_attr(self):
        self.assertEqual(dom_search('<a x="1">A</a><a>A</a>', 'a',
                                    ret=ResultParam('x', missing=MissingAttr.NoSkip)), ['1', None])
        self.assertEqual(dom_search('<a x="1">A</a><a>A</a>', 'a',
                                    ret=ResultParam(['x'], missing=MissingAttr.NoSkip)), [['1'], [None]])
        self.assertEqual(dom_search('<a x="1">A</a><a>A</a>', 'a',
                                    ret=ResultParam('x', missing=MissingAttr.SkipIfDirect)), ['1'])
        self.assertEqual(dom_search('<a x="1">A</a><a>A</a>', 'a',
                                    ret=ResultParam(['x'], missing=MissingAttr.SkipIfDirect)), [['1'], [None]])
        self.assertEqual(dom_search('<a x="1">A</a><a>A</a>', 'a',
                                    ret=ResultParam('x', missing=MissingAttr.SkipAll)), ['1'])
        self.assertEqual(dom_search('<a x="1">A</a><a>A</a>', 'a',
                                    ret=ResultParam(['x'], missing=MissingAttr.SkipAll)), [['1']])

