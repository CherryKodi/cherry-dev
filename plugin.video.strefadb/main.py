# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests, json, resolveurl , sys

from ptw.libraries import addon_utils as addon
from ptw.libraries import source_utils, dom_parser, client, cleantitle, cache

from ptw.debug import log_exception, log, start_trace, stop_trace, TRACE_ALL

_pluginName = sys.argv[0].replace('plugin://','')
_basePath = "special://home/addons/" + _pluginName + "resources/media/"
_resourcesPath = xbmc.translatePath(_basePath)
_default_background = _resourcesPath + "fanart.jpg"

s = requests.Session()

HEADERS = {
    'Host': 'strefadb.pl',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
    'Referer': 'https://strefadb.pl/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#

def CATEGORIES():
    addon.addDir('Lektor PL', '-', mode='Lektor', icon=_resourcesPath + "lektor.jpg" , thumb=_resourcesPath + "lektor.jpg", fanart=_default_background)
    addon.addDir('Napisy PL', '-', mode='Napisy', icon=_resourcesPath + "napisy.gif", thumb=_resourcesPath + "napisy.gif", fanart=_default_background)

def SUBCATEGORIES(mode):
    #Lektor
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    if mode == 'Lektor':
        addon.addDir('Dragon Ball', '-', mode='ListowanieLektor' , icon=_resourcesPath + "DB.png", thumb=_resourcesPath + "DB.png", fanart=_default_background)
        addon.addDir('Dragon Ball Z', '-', mode='ListowanieLektor', icon=_resourcesPath + "dbz.png", thumb=_resourcesPath + "dbz.png", fanart=_default_background)
        addon.addDir('Dragon Ball Kai', '-', mode='ListowanieLektor', icon=_resourcesPath + "dbkai.png", thumb=_resourcesPath + "dbkai.png", fanart=_default_background)
        addon.addDir('Dragon Ball GT', '-', mode='ListowanieLektor', icon=_resourcesPath + "dbgt.png", thumb=_resourcesPath + "dbgt.png", fanart=_default_background)
        addon.addDir('Dragon Ball Super', '-', mode='ListowanieLektor', icon=_resourcesPath + "dbs.png", thumb=_resourcesPath + "dbs.png", fanart=_default_background)
        addon.addDir('Dragon Ball Heroes', '-', mode='ListowanieLektor', icon=_resourcesPath + "dbh.png", thumb=_resourcesPath + "dbh.png", fanart=_default_background)
        addon.addDir('Kinowki', '-', mode='ListowanieLektor', icon=_resourcesPath + "kino.jpg", thumb=_resourcesPath + "kino.jpg", fanart=_default_background)
    #Napisy
    if mode == 'Napisy':
        addon.addDir('Dragon Ball', '-', mode='ListowanieNapisy', icon=_resourcesPath + "DB.png", thumb=_resourcesPath + "DB.png", fanart=_default_background)
        addon.addDir('Dragon Ball Z', '-', mode='ListowanieNapisy', icon=_resourcesPath + "dbz.png", thumb=_resourcesPath + "dbz.png", fanart=_default_background)
        addon.addDir('Dragon Ball Kai', '-', mode='ListowanieNapisy', icon=_resourcesPath + "dbkai.png", thumb=_resourcesPath + "dbkai.png", fanart=_default_background)
        addon.addDir('Dragon Ball GT', '-', mode='ListowanieNapisy', icon=_resourcesPath + "dbgt.png", thumb=_resourcesPath + "dbgt.png", fanart=_default_background)
        addon.addDir('Dragon Ball Super', '-', mode='ListowanieNapisy', icon=_resourcesPath + "dbs.png", thumb=_resourcesPath + "dbs.png", fanart=_default_background)
        addon.addDir('Dragon Ball Heroes', '-', mode='ListowanieNapisy', icon=_resourcesPath + "dbh.png", thumb=_resourcesPath + "dbh.png", fanart=_default_background)
        addon.addDir('Kinowki', '-', mode='ListowanieNapisy', icon=_resourcesPath + "kino.jpg", thumb=_resourcesPath + "kino.jpg", fanart=_default_background)

############################################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#

def list_episodes(nazwaSerii, wersja, fanart):
    lista = []
    lista_tytulow = []
    lista_linkow = []
    ocena = []

    cookie = cache.cache_get('strefadb_cookie')['value']
    if type(cookie) is dict:
        cookie = cookie['value']
    HEADERS['Cookie'] = cookie

    url = 'https://strefadb.pl/odcinki/' + nazwaSerii + '.html'
    result = s.get(url, headers=HEADERS).content
    test = client.parseDOM(result, 'ul', attrs={'class':'lista-odcinkow'})
    test = client.parseDOM(test, 'li')
    for item in test:
        if 'a href' in item and '?typ' not in item:
            lista.append(item)
    for item in lista:
        try:
            item = client.parseDOM(item, 'a')
            lista_tytulow.append(str(item[0]))
            test = str(lista_tytulow[-1])
            ocena.append(float(lista_tytulow[-1][-5:-1]))
            lista_tytulow[-1]=lista_tytulow[-1][:-7]
        except:
            pass
    i=1
    while i < len(lista_tytulow)+1:
        url = 'https://strefadb.pl/odcinki/' + nazwaSerii + '-' +str(i)+'.html?typ=' + wersja
        addon.addDir(str(i) + ' ' + str(lista_tytulow[i-1]), url, mode='ListowanieLinkow', fanart=fanart, rating=ocena[i-1])
        i+=1

def OdpalanieLinku():
    url = params['url']
    addon.PlayMedia(url)

############################################################################################################
#=########################################################################################################=#
#                                               GET PARAMS                                                 #
#=########################################################################################################=#

params = addon.get_params()
url = params.get('url')
name = params.get('name')
mode = params.get('mode')
iconimage = params.get('iconimage')

############################################################################################################
#=########################################################################################################=#
#                                                   MODES                                                  #
#=########################################################################################################=#

################################Lektor###########################

if mode == 'ListowanieLektor' or 'ListowanieNapisy':
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

if name == 'Dragon Ball' and mode == 'ListowanieLektor':
    list_episodes('dragon-ball', 'lektor', _resourcesPath + "db_art.jpg")

if name == 'Dragon Ball Z' and mode == 'ListowanieLektor':
    list_episodes('dragon-ball-z', 'lektor', _resourcesPath + "dbz_art.jpg")

if name == 'Dragon Ball Kai' and mode == 'ListowanieLektor':
    list_episodes('dragon-ball-kai', 'lektor', _resourcesPath + "dbkai_art.jpeg")

if name == 'Dragon Ball GT' and mode == 'ListowanieLektor':
    list_episodes('dragon-ball-gt', 'lektor', _resourcesPath + "dbgt_art.png")

if name == 'Dragon Ball Super' and mode == 'ListowanieLektor':
    list_episodes('dragonball-super', 'lektor', _resourcesPath + "dbs_art.jpg")

if name == 'Dragon Ball Heroes' and mode == 'ListowanieLektor':
    list_episodes('dragon-ball-heroes', 'lektor', _resourcesPath + "dbh_art.jpg")

if name == 'Kinowki' and mode == 'ListowanieLektor':
    lista = []
    lista_tytulow = []
    lista_linkow = []

    url = 'https://strefadb.pl/filmy-kinowe.html'
    result = client.request(url)
    lista_odcinkow = client.parseDOM(result, 'ul', attrs={'class':'lista-odcinkow'})
    lista_odcinkow = client.parseDOM(lista_odcinkow, 'li')

    for item in lista_odcinkow:
        if 'a href' in item and '?typ' not in item:
            lista.append(item)
    for item in lista:
        item2 = client.parseDOM(item, 'a')
        lista_tytulow.append(item2[0])
        item = client.parseDOM(item, 'a', ret='href')[0]
        lista_linkow.append(item)
    i=1
    while i < len(lista_tytulow)+1:
        url = 'https://strefadb.pl' + lista_linkow[i-1]
        addon.addDir(str(i) + ' ' + str(lista_tytulow[i-1]).replace('(', '| ocena odcinka: ('), url, mode='ListowanieLinkow', fanart=_resourcesPath + "kino_fanart.jpg")
        i+=1

################################Napisy##################

if name == 'Dragon Ball' and mode == 'ListowanieNapisy':
    list_episodes('dragon-ball', 'napisy', _resourcesPath + "db_art.jpg")

if name == 'Dragon Ball Z' and mode == 'ListowanieNapisy':
    list_episodes('dragon-ball-z', 'napisy', _resourcesPath + "dbz_art.jpg")

if name == 'Dragon Ball Kai' and mode == 'ListowanieNapisy':
    list_episodes('dragon-ball-kai', 'napisy', _resourcesPath + "dbkai_art.jpeg")

if name == 'Dragon Ball GT' and mode == 'ListowanieNapisy':
    list_episodes('dragon-ball-gt', 'napisy', _resourcesPath + "dbgt_art.png")
        
if name == 'Dragon Ball Super' and mode == 'ListowanieNapisy':
    list_episodes('dragonball-super', 'napisy', _resourcesPath + "dbs_art.jpg")

if name == 'Dragon Ball Heroes' and mode == 'ListowanieNapisy':
    list_episodes('dragon-ball-heroes', 'napisy', _resourcesPath + "dbh_art.jpg")

if name == 'Kinowki' and mode == 'ListowanieNapisy':
    lista = []
    lista_tytulow = []
    lista_linkow = []

    url = 'https://strefadb.pl/filmy-kinowe.html'
    result = client.request(url)
    lista_odcinkow = client.parseDOM(result, 'ul', attrs={'class':'lista-odcinkow'})
    lista_odcinkow = client.parseDOM(lista_odcinkow, 'li')

    for item in lista_odcinkow:
        if 'a href' in item and '?typ' not in item:
            lista.append(item)
    for item in lista:
        item2 = client.parseDOM(item, 'a')
        lista_tytulow.append(item2[0])
        item = client.parseDOM(item, 'a', ret='href')[0]
        lista_linkow.append(item)
    i=1
    while i < len(lista_tytulow)+1:
        url = 'https://strefadb.pl' + lista_linkow[i-1] + '?typ=napisy'
        addon.addDir(str(i) + ' ' + str(lista_tytulow[i-1]).replace('(', '| ocena odcinka: ('), url, mode='ListowanieLinkow', fanart=_resourcesPath + "kino_fanart.jpg")
        i+=1

if mode == None or url == None or len(url) < 1 :
    if xbmcplugin.getSetting(int(sys.argv[1]), 'user') == '':
        dialog = xbmcgui.Dialog()
        dialog.ok('Blad!', 'Wpisz dane do logowania w ustawieniach :)')
        sys.exit(0)
    else:
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0' }
        data ={"login" : str(xbmcplugin.getSetting(int(sys.argv[1]), 'user')), 'password': str(xbmcplugin.getSetting(int(sys.argv[1]), 'pass')),'signin': 'ok'}
        s.post('https://strefadb.pl/', data=data, headers=headers)
        cookie = s.cookies.get_dict()
        import ast
        cookie_string = "; ".join([str(x)+"="+str(y) for x,y in cookie.items()])
        cache.cache_insert('strefadb_cookie', str(cookie_string))
    CATEGORIES()

elif mode == 'Lektor':
    log('Mode Lektor')
    SUBCATEGORIES('Lektor')

elif mode == 'Napisy': 
    SUBCATEGORIES('Napisy')

elif mode == 'ListowanieLinkow':
    from urlparse import urlparse
    
    cookie = cache.cache_get('strefadb_cookie')
    if type(cookie) is dict:
        cookie = cookie['value']
    HEADERS['Cookie'] = cookie

    link = params['url']
    result = s.get(link, headers=HEADERS).content
    result = client.parseDOM(result, 'iframe', ret='src')
    url = result[0]
    o = urlparse(url)
    addon.addLink(str(o.netloc), url, mode='OdpalanieLinku')
    try:
        link = link + "&mirror=2"
        result = s.get(link, headers=HEADERS).content
        result = client.parseDOM(result, 'iframe', ret='src')
        url = result[0]
        o = urlparse(url)
        addon.addLink(str(o.netloc), url, mode='OdpalanieLinku')
    except:
        log_exception()
        pass

elif mode == 'OdpalanieLinku': 
    OdpalanieLinku()

###################################################################################

xbmcplugin.endOfDirectory(int(sys.argv[1]))