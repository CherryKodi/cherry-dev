# -*- coding: UTF-8 -*-
import urllib, urllib2, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon
import sys
from ptw.debug import log_exception, log, start_trace, stop_trace, TRACE_ALL

PY2 = sys.version_info[0] == 2
if PY2:
    from urlparse import parse_qs
else:
    from urllib.parse import parse_qs

def addDir(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='', genre='', year='', rating='', dateadded='', plot='', isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name)
    liz.setArt({
                'thumb': thumb,
                'icon': icon,
                'fanart': fanart,
                'poster': poster,
                'banner': banner,
                'clearart': clearart,
                'clearlogo': clearlogo
                })
    liz.setInfo("Video", {'title':name , 'genre': genre, 'year': year, 'rating': rating, 'dateadded': dateadded, 'plot': plot})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)

def addLink(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='', genre='', year='', rating='', dateadded='', plot='', isFolder=False, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name)
    liz.setArt({
            'thumb': thumb,
            'icon': icon,
            'fanart': fanart,
            'poster': poster,
            'banner': banner,
            'clearart': clearart,
            'clearlogo': clearlogo
            })
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)

def get_params():
    paramstring = sys.argv[2]
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict((k, vv[0]) for k, vv in parse_qs(paramstring).items())

def PlayMedia(link):
    import resolveurl
    try:
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Odtwarzanie', 'Odpalanie linku...')
        url = resolveurl.resolve(link)
        if url is False:
            raise ValueError('Nie udało się wyciągnąć linku')
        pDialog.close()
        xbmc.Player().play(str(url))
    except Exception as e:
        pDialog.close()
        xbmcgui.Dialog().ok('Error', 'Błąd odpalania linku! %s' % e)
        log_exception()