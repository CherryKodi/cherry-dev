# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests, json
import sys

PY2 = sys.version_info[0] == 2
if PY2:
    from urlparse import parse_qs
    from urllib import urlencode
else:
    from urllib.parse import parse_qs, urlencode

from ptw.debug import log_exception, log, start_trace, stop_trace, TRACE_ALL
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
    global s
    s, content = obj.ListaKanalow()
    content = json.loads(content)
    for item in content:
        addDir(name=item['title'], url=item['url'], mode='play', thumb=item['icon'], isFolder=False)

def OdpalanieLinku(url):
    try:
        global s
        s, content = obj.ListaKanalow()
        link = obj.Link(url, s)
        xbmc.Player().play(str(link).replace("rtmp://$OPT:rtmp-raw=", ""))
    except:
        log_exception()

def get_params():
    paramstring = sys.argv[2]
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict((k, urllib.unquote_plus(vv[0])) for k, vv in parse_qs(paramstring).items())

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
