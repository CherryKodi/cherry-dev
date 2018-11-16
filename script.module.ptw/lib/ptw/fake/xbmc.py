# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

from enum import IntEnum
from datetime import datetime


LOG_LEVEL_NONE          = -1 # nothing at all is logged
LOG_LEVEL_NORMAL        =  0 # shows notice, error, severe and fatal
LOG_LEVEL_DEBUG         =  1 # shows all
LOG_LEVEL_DEBUG_FREEMEM =  2 # shows all + shows freemem on screen

LOGDEBUG   = 0
LOGINFO    = 1
LOGNOTICE  = 2
LOGWARNING = 3
LOGERROR   = 4
LOGSEVERE  = 5
LOGFATAL   = 6
LOGNONE    = 7


def log(msg, level=LOGDEBUG):
    names = ('DEBUG', 'INFO', 'NOTICE', 'WARNING',
             'ERROR', 'SEVERE', 'FATAL', 'NONE', )
    name = names[level] if 0 <= level < len(names) else '???'
    ts = datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]
    indent = ' ' * 23
    print('{time} {lvl:>8s}: {msg}'.format(time=ts, lvl=name, msg=msg.replace('\n', '\n'+indent)))


