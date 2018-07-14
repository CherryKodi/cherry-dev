# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

import sys
import xbmcaddon

PY = sys.version_info[0]
PY2 = PY == 2
PY3 = PY == 3

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')

