# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests,json
from resources.lib.libraries import source_utils, dom_parser, client, cleantitle
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
    addDir("Kategorie", "", 20, '','','','','','')
    addDir("Najnowsze filmy", 'https://dokumentalne.net/najnowsze-filmy/', 10, '','','','','','')
    addDir("Filmy w HD", 'https://dokumentalne.net/category/hd-filmy/', 10, '','','','','','')
    addDir("Wszystkie filmy", 'https://dokumentalne.net/category/wszystkie-filmy/', 10, '','','','','','')

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
        link = "https://dokumentalne.net/?s="+search
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
    kategorie = {"Astronomiczne" : "https://dokumentalne.net/category/astronomiczne-kosmos/",
                 "Biograficzne" : "https://dokumentalne.net/category/biograficzne/",
                 "Filmy HD" : "https://dokumentalne.net/category/hd-filmy/",
                 "Historyczne" : "https://dokumentalne.net/category/historyczne/",
                 "Katastroficzne" : "https://dokumentalne.net/category/katastroficzne/",
                 "Kryminalne" : "https://dokumentalne.net/category/kryminalne/",
                 "Motoryzacyjne": "https://dokumentalne.net/category/motoryzacyjne/",
                 "Naukowe": "https://dokumentalne.net/category/naukowe/",
                 "Podróżnicze" : "https://dokumentalne.net/category/podroznicze/",
                 "Przyrodnicze" : "https://dokumentalne.net/category/przyrodnicze/",
                 "Psychologiczne" : "https://dokumentalne.net/category/psychologiczne/",
                 "Spoleczeństwo" : "https://dokumentalne.net/category/spoleczenstwo/",
                 "Technologia" : "https://dokumentalne.net/category/technologia/",
                 "Wojenne" : "https://dokumentalne.net/category/wojenne/"
                 }
    for item in kategorie:
        addDir(str(item), str(kategorie[item]), 10, '','','','','','')
        
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
        nastepna = client.parseDOM(nawigacja, 'a', ret='href')[-2]
        nawigacja = client.parseDOM(nawigacja, 'a', attrs={'class':'nextpostslink'})
    except:
        nawigacja = ""
    result = client.parseDOM(result, 'div', attrs={'class':'entry-content'})
    
    
    for item in result:
        item2 = client.parseDOM(item, 'div', attrs={'class':'picture-content '})
        if len(item2) == 0 :
            continue
        opis = client.parseDOM(item, 'div', attrs={'class':'excerpt sub-lineheight'})[0]
        link = client.parseDOM(item2, 'a', ret='href')[0]
        nazwa = client.parseDOM(item2, 'a', ret='title')[0]
        obraz = client.parseDOM(item2, 'img', ret='src')[0]
        addLink(str(nazwa), str(link), 6, str(obraz), str(obraz),str(opis),'','')
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
        url = client.parseDOM(result, 'source', ret='src')[0]
        if str(url).startswith("//"):
            url = url.replace("//", "http://")
    except:
        url = client.parseDOM(result, 'iframe', ret='src')[0]
        if str(url).startswith("//"):
            url = url.replace("//", "http://")
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
    
###################################################################################
xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))