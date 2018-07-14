# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests,json
from ptw.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys
from HTMLParser import HTMLParser

reload(sys)
sys.setdefaultencoding('utf8')
url = ""
#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#
def CATEGORIES():
    addDir("Szukaj", '', 1, '','','','','','')
    addDir("Kanaly", "", 21, '','','','','','')
    addDir("Kategorie", "", 20, '','','','','','')
    addDir("Polecane", 'http://www.filmydokumentalne.eu/polecane/', 10, '','','','','','')
    addDir("Ranking", 'http://www.filmydokumentalne.eu/ranking/', 10, '','','','','','')
    addDir("Najnowsze", 'http://www.filmydokumentalne.eu/najnowsze-filmy/', 10, '','','','','','')
def SUBCATEGORIES(mode):
    debug=1
###################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#

def mySearch():
    #import pydevd
    #pydevd.settrace(stdoutToServer=True, stderrToServer=True)
    keyb = xbmc.Keyboard('', "Wyszukiwarka")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0 :
        search = keyb.getText()
        myParam = str(urllib.quote(search)).strip()
        link = "http://www.filmydokumentalne.eu/?s="+search
        ListujFilmy(link)
    else:
        CATEGORIES()

def addDir(name, url, mode, banner, thumb, fanart, opis, gatunek, rating, isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, banner, thumbnailImage=thumb)
    liz.setArt({'thumb': thumb,
                'banner': banner,
                'fanart': fanart})
    liz.setInfo("Video", {'title':name , 'genre':gatunek, 'rating': rating, 'plot': opis})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def addLink(name, url, mode, iconimage, thumb, opis, gatunek, rating, isFolder=False, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconimage, thumbnailImage=thumb)
    url = thumb
    liz.setArt({'thumb': thumb,
                'icon': iconimage,
                'fanart': url})
    liz.setInfo("Video", {'title':name , 'genre':gatunek, 'rating': rating, 'plot': opis})
    liz.setProperty("IsPlayable" , "true")
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def ListujKategorie():
    kategorie = {"Astrofizyka" : "http://www.filmydokumentalne.eu/kategorie/astrofizyka/",
                 "Biograficzne" : "http://www.filmydokumentalne.eu/kategorie/biograficzne/",
                 "Dusze czyśćcowe" : "http://www.filmydokumentalne.eu/kategorie/dusze-czysccowe/",
                 "Ewangelizacyjne" : "http://www.filmydokumentalne.eu/kategorie/ewangelizacyjne/",
                 "Ewolucja" : "http://www.filmydokumentalne.eu/kategorie/ewolucja-kategorie/",
                 "Gadżeciarskie" : "http://www.filmydokumentalne.eu/kategorie/gadzeciarskie/",
                 "Historyczne": "http://www.filmydokumentalne.eu/kategorie/historyczne/",
                 "II Wojna Światowa": "http://www.filmydokumentalne.eu/kategorie/ii-wojna-swiatowa-kategorie/",
                 "Katastroficzne" : "http://www.filmydokumentalne.eu/kategorie/katastroficzne/",
                 "Kryminalne" : "http://www.filmydokumentalne.eu/kategorie/kryminalne/",
                 "Kultura i sztuka" : "http://www.filmydokumentalne.eu/kategorie/kultura-i-sztuka/",
                 "Lotnictwo" : "http://www.filmydokumentalne.eu/kategorie/lotnictwo-kategorie/",
                 "Medycyna" : "http://www.filmydokumentalne.eu/kategorie/medycyna/",
                 "Motoryzacja" : "http://www.filmydokumentalne.eu/kategorie/motoryzacja-kategorie/",
                 "Nauka" : "http://www.filmydokumentalne.eu/kategorie/nauka/",
                 "Obcojezyczne" : "http://www.filmydokumentalne.eu/kategorie/obcojezyczne/",
                 "Paranormalne" : "http://www.filmydokumentalne.eu/kategorie/paranormalne-2/",
                 "Podróżnicze" : "http://www.filmydokumentalne.eu/kategorie/podroznicze/",
                 "Polityczne" : "http://www.filmydokumentalne.eu/kategorie/polityczne/",
                 "Pozostale" : "http://www.filmydokumentalne.eu/kategorie/pozostale/",
                 "Przetrwanie" : "http://www.filmydokumentalne.eu/kategorie/przetrwanie-kategorie/",
                 "Przyrodnicze" : "http://www.filmydokumentalne.eu/kategorie/przyrodnicze/",
                 "Religijne" : "http://www.filmydokumentalne.eu/kategorie/religijne/",
                 "Sport" : "http://www.filmydokumentalne.eu/kategorie/sport/",
                 "Spoleczenstwo" : "http://www.filmydokumentalne.eu/kategorie/spoleczenstwo/",
                 "Technika" : "http://www.filmydokumentalne.eu/kategorie/technika/",
                 "Wojskowe" : "http://www.filmydokumentalne.eu/kategorie/wojskowe/",
                 }
    for item in kategorie:
        addDir(str(item), str(kategorie[item]), 10, '','','','','','')
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def ListujKanaly():
    kanaly = {"Animal Planet" : "http://www.filmydokumentalne.eu/kanaly/animal-planet/",
                 "BBC" : "http://www.filmydokumentalne.eu/kanaly/bbc/",
                 "Canal+" : "http://www.filmydokumentalne.eu/kanaly/canal/",
                 "DC" : "http://www.filmydokumentalne.eu/kanaly/dc/",
                 "FokusTV" : "http://www.filmydokumentalne.eu/kanaly/fokustv/",
                 "HBO" : "http://www.filmydokumentalne.eu/kanaly/hbo/",
                 "History Channel": "http://www.filmydokumentalne.eu/kanaly/history-channel/",
                 "NG": "http://www.filmydokumentalne.eu/kanaly/ng-kanaly/",
                 "Planete" : "http://www.filmydokumentalne.eu/kanaly/planete/",
                 "Polsat" : "http://www.filmydokumentalne.eu/kanaly/polsat/",
                 "Polsat Play" : "http://www.filmydokumentalne.eu/kanaly/polsat-play/",
                 "Pozostale" : "http://www.filmydokumentalne.eu/kanaly/pozostale-kanaly/",
                 "TVN" : "http://www.filmydokumentalne.eu/kanaly/tvn/",
                 "TVP" : "http://www.filmydokumentalne.eu/kanaly/tvp/",
                 }
    for item in kanaly:
        addDir(str(item), str(kanaly[item]), 10, '','','','','','')
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def ListujFilmy(url = ""):
    try:
        url = urllib.unquote_plus(params['url'])
    except:
        pass
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    try:
        nawigacja = client.parseDOM(result, 'div', attrs={'class':'wp-pagenavi'})
        nastepna = client.parseDOM(nawigacja, 'a', ret='href')[-1]
        nawigacja = client.parseDOM(nawigacja, 'a', attrs={'class':'nextpostslink'})
    except:
        nawigacja = ""
    result = client.parseDOM(result, 'div', attrs={'id':'left'})
    result = client.parseDOM(result, 'div', attrs={'id':'news'})
    for item in result:
        link = client.parseDOM(item, 'a', ret='href')[0]
        nazwa = client.parseDOM(item, 'a')[0]
        addLink(str(nazwa).replace("„", "").replace('”', ''), str(link), 6, "", "","",'','')
    if len(nawigacja)>0:
        addDir("Nastepna strona", str(nastepna), 10, '','','','','','')
        
def ListujLinki():
    #import pydevd
    #pydevd.settrace(stdoutToServer=True, stderrToServer=True)
    url = urllib.unquote_plus(params['url'])
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    result = client.parseDOM(result, 'table', attrs={'class':'table table-bordered'})
    linki = client.parseDOM(result, 'a', ret='href')
    for item in linki:
        temp = client.request(str(item))
        link = client.parseDOM(temp, 'iframe', ret='src')[0]
        hostDict = resolveurl.relevant_resolvers(order_matters=True)
        hostDict = [i.domains for i in hostDict if not '*' in i.domains]
        hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
        hostDict = [x for y,x in enumerate(hostDict) if x not in hostDict[:y]]
        valid, host = source_utils.is_host_valid(str(link), hostDict)
        if valid == False:
            continue
        addLink("[B]"+host+"[/B]", link, 6, "", "", "", "", "")
###################################################################################
#=########################################################################################################=#
#                                               GET PARAMS                                                 #
#=########################################################################################################=#    
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
        
###################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#
if mode == None :
    CATEGORIES()
    
elif mode == 1 :
    mySearch()
    
#####MENU######
elif mode == 20 :
    ListujKategorie()
elif mode == 21 :
    ListujKanaly()
elif mode == 10 :
    ListujFilmy()

elif mode == 11 :
    ListujLinki()
   
elif mode == 6 : 
    url = urllib.unquote_plus(params['url'])
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    try:
        url = client.parseDOM(result, 'source', ret='src')[1]
        if str(url).startswith("//"):
            url = url.replace("//", "http://")
    except:
        url = client.parseDOM(result, 'iframe', ret='src')[1]
        if str(url).startswith("//"):
            url = url.replace("//", "http://")
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
    
###################################################################################
xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))