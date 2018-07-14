# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests, json
import sys

PY2 = sys.version_info[0] == 2
if PY2:
    from urlparse import parse_qs
else:
    from urllib.parse import parse_qs

from ptw.debug import log_exception, log, start_trace, stop_trace, TRACE_ALL
import wizja

obj = wizja.WizjaTvApi()
s = requests.Session()

def CATEGORIES():
    WizjaTV()

def addDir(name, url, mode, thumb, fanart, opis, isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, thumbnailImage=thumb)
    liz.setArt({'thumb': thumb,
                'fanart': fanart})
    liz.setInfo("Video", {'title':name })
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def WizjaTV():
    global s
    s, content = obj.ListaKanalow()
    content = json.loads(content)
    for item in content:
        addDir(item['title'],item['url'] , 6, item['icon'],'','', False)

def OdpalanieLinku():
    try:
        global s
        url = urllib.unquote_plus(params['url'])
        s, content = obj.ListaKanalow()
        link = obj.Link(url,s)
        xbmc.Player().play(str(link).replace("rtmp://$OPT:rtmp-raw=", ""))
    except:
        log_exception()
        pass

def get_params():
    paramstring = sys.argv[2]
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict((k, vv[0]) for k, vv in parse_qs(paramstring).items())

params = get_params()
url = None
name = None
thumb = None
mode = None
iconimage = None

try:
    url = urllib.unquote_plus(params['url'])
except:
    pass
try:
    name = params.get('name')
except:
    pass
try:
    mode = int(params.get('mode'))
except:
    mode = None
    log_exception()
    pass
try:
    iconimage = urllib.unquote_plus(params['iconimage'])
except:
    pass

if mode == None :
    CATEGORIES()
elif mode == 6 : 
    OdpalanieLinku()

xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))