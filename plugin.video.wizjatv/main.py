# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests, json
import sys

from ptw.debug import log_exception, log, start_trace, stop_trace, TRACE_ALL

reload(sys)
sys.setdefaultencoding('utf8')

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

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
    import wizja
    s = requests.Session()
    obj = wizja.WizjaTvApi()
    s,content = obj.ListaKanalow(s)
    content = json.loads(content)
    for item in content:
        addDir(item['title'],item['url'] , 6, item['icon'],'','', False)

def odpalanieLinku():
    try:
        import wizja
        obj = wizja.WizjaTvApi()
        s = requests.Session()
        url = urllib.unquote_plus(params['url'])
        s,content = obj.ListaKanalow(s)
        link = obj.Link(url,s)
        xbmc.Player().play(str(link).replace("rtmp://$OPT:rtmp-raw=", ""))
    except:
        log_exception()
        pass

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2 :
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/') :
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)) :
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

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
    name = urllib.unquote_plus(params['name'])
except:
    pass
try:
    mode = int(params['mode'])
except:
    pass
try:
    iconimage = urllib.unquote_plus(params['iconimage'])
except:
    pass

if mode == None :
    CATEGORIES()
elif mode == 6 : 
    odpalanieLinku()

xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))