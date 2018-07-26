# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

import xbmc
from .info import addon_name



class Log(object):
    r"""
    Parameters
    ----------
    level : int or None, default None
        Kodi log level (one of xbmc.LOG*) or None for default level (xbmc.LOGDEBUG).

    Attributes
    ----------
    level : int
        Kodi log level (one of xbmc.LOG*) for default level (xbmc.LOGDEBUG).
    """

    def __init__(self, level=None):
        self.level = xbmc.LOGDEBUG if level is None else level


    def __call__(self, msg, level=None):
        r"""
        Log message in Kodi/XBMC log.

        Parameters
        ----------
        msg : str
            String message to log.
        level : int or None, default None
            Kodi log level (one of xbmc.LOG*) or None for default is used.
        """
        if level is None:
            level = self.level
        msg = str(msg)
        msg = '[{addon}] {msg}'.format(addon=addon_name, msg=msg)
        xbmc.log(msg, level)


    #def log(self, level, *args, sep=' ', end='\n'):  only in Py3
    def log(self, level, *args, **kwargs):
        r"""
        Log all arguments at level `level`.

        Parameters
        ----------
        level : int or None, default None
            Kodi log level (one of xbmc.LOG*) or None for default is used.
        *args
            List of arguments to log. Any types.
        sep : str, default ' '
            String inserted between values, default a space.
        end : str, default '\n'
            String appended after the last value, default a newline. IGNORED!
        file
            IGNORED
        flush
            IGNORED

        Print-like function (see help(print) in Python3) with log output.
        """
        approved = set(('sep', 'end', 'file', 'flush'))
        if set(kwargs) - approved:
            raise TypeError('{0} is an invalid keyword argument for this function'.format(
                *set(kwargs) - approved))
        sep = kwargs.get('sep', ' ')
        self(sep.join(str(a) for a in args), level=level)


    def debug(self, *args, **kwargs):
        r"""
        Log all arguments at level xbmc.LOGDEBUG.

        See: log().
        """
        self.log(xbmc.LOGDEBUG, *args, **kwargs)


    def info(self, *args, **kwargs):
        r"""
        Log all arguments at level xbmc.LOGINFO.

        See: log().
        """
        self.log(xbmc.LOGINFO, *args, **kwargs)


    def notice(self, *args, **kwargs):
        r"""
        Log all arguments at level xbmc.LOGNOTICE.

        See: log().
        """
        self.log(xbmc.LOGNOTICE, *args, **kwargs)


    def warning(self, *args, **kwargs):
        r"""
        Log all arguments at level xbmc.LOGWARNING.

        See: log().
        """
        self.log(xbmc.LOGWARNING, *args, **kwargs)

    warn = warning


    def error(self, *args, **kwargs):
        r"""
        Log all arguments at level xbmc.LOGERROR.

        See: log().
        """
        self.log(xbmc.LOGERROR, *args, **kwargs)


    def severe(self, *args, **kwargs):
        r"""
        Log all arguments at level xbmc.LOGSEVERE.

        See: log().
        """
        self.log(xbmc.LOGSEVERE, *args, **kwargs)


    def fatal(self, *args, **kwargs):
        r"""
        Log all arguments at level xbmc.LOGFATAL.

        See: log().
        """
        self.log(xbmc.LOGFATAL, *args, **kwargs)

