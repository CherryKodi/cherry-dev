# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function
import sys
PY2 = sys.version_info[0] == 2

if PY2:
    from unittest import TestCase as UTestCase
    class TestCaseSubTest(object):
        def __init__(self, test, title):
            self.test, self.title = test, title
        def __enter__(self):
            return self
        def __exit__(self, type, value, traceback):
            pass
    class TestCase(UTestCase):
        def subTest(self, title):
            return TestCaseSubTest(self, title)
else:
    from unittest import TestCase
