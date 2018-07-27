# -*- coding: UTF-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests, json
import sys
from ptw.libraries.addon_utils import get_params

PY2 = sys.version_info[0] == 2
if PY2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode


from ptw.debug import log_exception, log
import wizja

obj = wizja.WizjaTvApi()
s = requests.Session()

def CATEGORIES():
    WizjaTV()

def addDir(name, url, mode, thumb, fanart='', opis='', isFolder=True, total=1):
    u = '{}?{}'.format(sys.argv[0], urlencode(dict(url=url, mode=mode, name=name)))
    liz = xbmcgui.ListItem(name, thumbnailImage=thumb)
    liz.setArt({'thumb': thumb,
                'fanart': fanart})
    liz.setInfo("Video", {'title': name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def WizjaTV():
    channel_list = sorted(obj.channel_list(), key=lambda ch: ch.name)
    for ch in channel_list:
        addDir(name=ch.name, url=ch.url, mode='play', thumb=ch.icon, isFolder=False)

def OdpalanieLinku(url):
    link = obj.video_link(url)
    if link:
        xbmc.Player().play(link)


params = get_params()
url = params.get('url')
name = params.get('name')
mode = params.get('mode')
iconimage = params.get('iconimage')

if mode is None:
    CATEGORIES()
elif mode == 'play':
    OdpalanieLinku(url)

xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))
