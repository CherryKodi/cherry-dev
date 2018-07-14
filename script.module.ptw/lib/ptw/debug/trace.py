# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

import sys
import xbmc
from .info import PY2, addon_name

if not PY2:
    basestring = str


#: Trace all calls (without returns). Uses sys.settrace().
TRACE_CALL = 1
#: Trace all events. Uses sys.setprofile().
TRACE_ALL  = 2


class TraceLogger(object):
    """
    Trace logger.

    Logs every call. Every return if set.

    Parameters
    ----------
    details: int
        Trace details (TRACE_CALL or TRACE_ALL)
    level : int or None, optional
        Kodi log level (xbmc.LOGINFO...) or None (xbmc.LOGDEBUG is used).
    use_old_trace : bool, optional
        True if old trace also should be used.
    """

    def __init__(self, details=TRACE_CALL, level=None, use_old_trace=False):
        self.level = level
        self.use_old_trace = use_old_trace
        self.__old_trace = None
        self.__runing = False
        self.__details = details


    @property
    def details(self):
        """Trace details (TRACE_CALL or TRACE_ALL). Can't be changed."""
        return self.__details


    @property
    def running(self):
        """True if tracing."""
        return self.__runing


    def _should_skip(self, frame):
        f, fname = frame.f_back, frame.f_code.co_filename
        while f:
            if fname.startswith('/usr/lib/'):
                return True
            if 'addons/script.module.ptw/lib/ptw/debug' in fname:
                return True
            f = f.f_back
        return False


    def log_trace(self, frame, event, arg):
        """
        Trace callback. See sys.settrace().
        """
        if event in ('c_call', 'c_return', 'c_exception'):
            return
        if self._should_skip(frame):
            return
        fc = frame.f_code
        fname, lno, func = fc.co_filename, fc.co_firstlineno, fc.co_name
        anames = fc.co_varnames
        pre = '[{addon}][STACK] '.format(addon=addon_name)
        def geta(k):
            try:
                v = frame.f_locals.get(k, frame.f_globals.get(k, '?????'))
                if isinstance(v, basestring):
                    return v[:100]
                if isinstance(v, list):
                    if v and isinstance(v[0], basestring):
                        return list(s[:100] if isinstance(s, basestring) else s for s in v[:50])
                    return v[:50]
                return v
            except:
                xbmc.log('{pre}Getting varaible "{var}" failed.'.format(pre=pre, var=k), xbmc.LOGDEBUG)
                return '???!!'
        sargs = ', '.join('{k}={v!r}'.format(k=k, v=geta(k)) for k in anames)
        msg = '{pre}{indent}{fname}:{lno}:\n{prespace}{indent}{func}({args})\n'.format(
            addon=addon_name, pre=pre, prespace=' '*(len(pre) - 4),
            fname=fname, lno=lno, func=func, args=sargs, indent='  '*fc.co_stacksize)
        xbmc.log(msg, xbmc.LOGDEBUG if self.level is None else self.level)
        if self.use_old_trace and self.__old_trace:
            self.__old_trace(frame, event, arg)
        # returns None – the scope shouldn’t be traced


    def start(self):
        """Start traceing."""
        #xbmc.log('[XXX] Starting! ' + str(self.__details), xbmc.LOGNOTICE)
        if not self.__runing:
            if self.__details == TRACE_CALL:
                self.__old_trace = sys.gettrace()
                sys.settrace(self.log_trace)
            elif self.__details == TRACE_CALL:
                self.__old_trace = sys.getprofile()
                sys.setprofile(self.log_trace)
            else:
                assert False, 'Incorect details level ({})'.format(self.__details)
                return
            self.__runing = True


    def stop(self):
        """Stop traceing."""
        #xbmc.log('[XXX] Stopping!', xbmc.LOGNOTICE)
        if self.__runing:
            if self.__details == TRACE_CALL:
                sys.settrace(self.__old_trace)
            elif self.__details == TRACE_CALL:
                sys.setprofile(self.__old_trace)
            else:
                assert False, 'Incorect details level ({})'.format(self.__details)
            self.__old_trace = None
            self.__runing = False



global_trace = None


def start_trace(details=TRACE_CALL, level=None):
    """
    Start trace logger.

    Logs every call. Every return if set.

    Parameters
    ----------
    details: int
        Trace details (TRACE_CALL or TRACE_ALL)
    level : int or None, optional
        Kodi log level (xbmc.LOGINFO...) or None (xbmc.LOGDEBUG is used).
    """
    global global_trace
    if not global_trace:
        global_trace = TraceLogger(details=details, level=level)
        global_trace.start()


def stop_trace():
    """
    Stop trace logger.
    """
    global global_trace
    if global_trace:
        global_trace.stop()
        global_trace = None


