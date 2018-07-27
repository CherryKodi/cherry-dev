# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import json
import re
import urllib

from ptw import PY2
import xbmcaddon
import xbmcgui
from ptw.debug import log_exception, log
from ptw.libraries import client
from ptw import dom
from ptw.utils import regex
import requests
import json

if PY2:
    from urlparse import parse_qs, urljoin, urlparse
    from urllib import urlencode, unquote_plus
else:
    from urllib.parse import parse_qs, urlencode, urljoin, urlparse, unquote_plus




# --- miejsca na części wspólne, które zostaną za chwilę wyniesione do PTW ---


def settiing_name(var, name=None):
    if name:
        return '_'.join((str(name), var))
    return var

def ptwSession(name=None, cookies=True, useProxy=False):
    sess = requests.Session()
    if useProxy:
        sess.proxies = dict(http='66.70.147.195:3128')  # TODO: use settings (name, default)
    if cookies is True:
        cookies = xbmcaddon.Addon().getSetting(settiing_name('cookies', name=name))
        if cookies:
            sess.cookies = requests.utils.cookiejar_from_dict(json.loads(cookies))
    elif cookies:
        sess.cookies = cookies
    return sess

def get(url, params=None, **kwargs):
    ptwSession().get(url=url, params=params, **kwargs)

def post(url, data=None, json=None, **kwargs):
    ptwSession().post(url=url, data=data, json=json, **kwargs)


# --- plugin ---


class Channel(object):
    r'''Channel desctiption'''
    def __init__(self, name, url, icon):
        self.name, self.url, self.icon = name, url, icon
    # --- log & debug only ---
    def __str__(self):
        return self.name
    def __repr__(self):
        return 'Channel({!r}, {!r}, {!r})'.format(self.name, self.url, self.icon)


class WizjaTvApi(PtwHttp):

    MAIN_URL = 'http://wizja.tv/'
    LOGIN_URL = MAIN_URL + 'users/index.php'
    ICON_URL = MAIN_URL + 'logo.png'
    CHANNELS_URL = MAIN_URL
    CHANNEL_PAGE_URL = MAIN_URL + 'watcher.php?id={id}'
    CHANNEL_REDIR_URL = MAIN_URL + 'porter.php?ch={id}'

    re_chan_name = regex(r'/(?P<chan>[^/]*?)\.[^.]*$')  # from <img src>
    re_chan_id = regex(r'id=(?P<id>\d+)')  # from <a href> (from channel url)
    re_premium = regex(r'Premium aktywne.*?<b>(?:<.*?>)*(?P<premium>.*?)<')
    re_rtmp_src = regex(r'parameters\s*=\s*\{.*?src:\s*"(?P<rtmp>.*?)"')

    def __init__(self):
        self.sess = ptwSession()
        self.logged = False
        self.premium = False

    def hasCookies(self):
        """Returns True if cookies are present"""
        return bool(xbmcaddon.Addon().getSetting('cookies'))

    def _check_if_logged(self, page):
        r"""Cehc if logged, set logged flag."""
        text = page.text
        self.logged = '?logout' in text
        # get premium date, if fail, set True if tag found
        self.premium = self.re_premium(text).premium or 'Premium aktywne' in text
        return self.logged

    def login(self):
        r"""Login using settings."""
        addon = xbmcaddon.Addon()
        user = addon.getSetting('username')
        password = addon.getSetting('password')

        params = {'user_name': user, 'user_password': password, 'login': 'Zaloguj'}
        page = self.sess.post(self.LOGIN_URL, data=params)
        self._check_if_logged(page)
        log.info('Login: user {user}, loagged {logged}, premium {premium}'.format(
            user=user, logged=self.logged, premium=self.premium))
        if not self.logged:
            xbmcgui.notification('WizjaTV', 'Logowanie nieudane', xbmcgui.NOTIFICATION_ERROR)

        cookies = page.cookies.get_dict()
        # requests.utils.dict_from_cookiejar(page.cookies)
        addon.setSetting('cookies', json.dumps(cookies))
        return self.logged

    def channel_list(self):
        r"""Get WizjaTV channel list."""
        log.debug("WizjaTvApi.getChannelsList")
        page = self.sess.get(self.CHANNELS_URL)
        return list(Channel(name=self.re_chan_name(src).chan.upper(),
                            url=urljoin(self.CHANNELS_URL, href),
                            icon=urljoin(self.CHANNELS_URL, src))
                    for (href,), (src,)
                    in dom.select(page, 'table[width] a[href*=watch](href) img(src)'))

    def video_link(self, url):
        r"""Get RTMP link to video."""
        log("WizjaTvApi.getVideoLink")

        # Login
        if not self.logged:
            self.login()

        # Find URL to page with RTMP
        id = self.re_chan_id(url).id
        page = self.sess.get(url)
        iframes = dom.select(page, 'iframe[name="player"]')
        if not iframes:
            log.info('No iframe in {}.'.format(url))
            return None
        url = urljoin(url, iframes[0].attr.src)

        # Get RTMP link
        page = self.sess.get(url)
        match = self.re_rtmp_src(page.text)
        if not match:
            return None

        url = urlparse(unquote_plus(match.rtmp))
        query = urlencode(dict((k, v[0])
                             for k, v in parse_qs(url.query).items()
                             if k in ('event', 'token', 'user')))
        pp = url.path.split('/')
        url = 'rtmp://{url.netloc}/{pp[1]}?{query} app={pp[1]}?{query} ' \
                'playpath={pp[2]}?{query} swfVfy=1 flashver=LNX/25,0,0,12 ' \
                'timeout=25 swfUrl=https://wizja.tv/player/StrobeMediaPlayback_v4.swf ' \
                'live=true pageUrl=https://wizja.tv/watch.php?id={id}'.format(
                    url=url, pp=pp, query=query, id=id)
        log.info('rtmp link', url)
        return url

