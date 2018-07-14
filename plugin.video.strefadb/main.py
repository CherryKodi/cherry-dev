# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests
from ptw.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys
import json

reload(sys)
sys.setdefaultencoding('utf8')

pluginName=sys.argv[0].replace('plugin://','')
s = requests.Session()
basePath = "special://home/addons/"+pluginName+"resources/media/"
resourcesPath = xbmc.translatePath(basePath)

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#
def CATEGORIES():
    addDir('Lektor PL', '-', 3, resourcesPath + "lektor.jpg" ,None,'', True)
    addDir('Napisy PL', '-', 4, resourcesPath + "napisy.gif",None,'', True)
def SUBCATEGORIES(mode):
    #Lektor
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    if mode == 3:
        addDir('Dragon Ball', '-', 5, resourcesPath + "DB.png",None,'', True)
        addDir('Dragon Ball Z', '-', 5, resourcesPath + "dbz.png",None,'', True)
        addDir('Dragon Ball Kai', '-', 5, resourcesPath + "dbkai.png",None,'', True)
        addDir('Dragon Ball GT', '-', 5, resourcesPath + "dbgt.png",None,'', True)
        addDir('Dragon Ball Super', '-', 5, resourcesPath + "dbs.png",None,'', True)
        addDir('Dragon Ball Heroes', '-', 5, resourcesPath + "dbh.png",None,'', True)
        addDir('Kinowki', '-', 5, resourcesPath + "kino.jpg",None,'', True)
    #Napisy
    if mode == 4:
        addDir('Dragon Ball', '-', 6, resourcesPath + "DB.png",None,'', True)
        addDir('Dragon Ball Z', '-', 6, resourcesPath + "dbz.png",None,'', True)
        addDir('Dragon Ball Kai', '-', 6, resourcesPath + "dbkai.png",None,'', True)
        addDir('Dragon Ball GT', '-', 6, resourcesPath + "dbgt.png",None,'', True)
        addDir('Dragon Ball Super', '-', 6, resourcesPath + "dbs.png",None,'', True)
        addDir('Dragon Ball Heroes', '-', 6, resourcesPath + "dbh.png",None,'', True)
        addDir('Kinowki', '-', 6, resourcesPath + "kino.jpg",None,'', True)
        
###################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#
def mySearch():
    keyb = xbmc.Keyboard('', 'XBMC Search')
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0 :
        search = keyb.getText()
        myParam = str(urllib.quote(search)).strip()
        addDir(myParam, 'myUrl', 2, 'other.jpg', False)
    else:
        CATEGORIES()
    
def myOther():
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('XBMC', 'Hello World')
    
def addDir(name, url, mode, iconimage, thumb, rating, isFolder=True, total=1, plot = ''):
    if thumb == None:
        thumb = resourcesPath + "fanart.jpg"
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconimage, thumbnailImage=thumb)
    url = thumb
    liz.setArt({'thumb': iconimage,
                'icon': iconimage,
                'fanart': thumb})
    liz.setInfo("Video", {'title':name , 'genre':'', 'rating': rating, 'plot': ''})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

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

#######################Funkcje ladujace listy odcinkow###########
def list_episodes(nazwaSerii,wersja,obrazek):
    import json
    basePath = "special://temp/cookie.txt"
    path = xbmc.translatePath(basePath)
    with open(path, 'r') as f:
        cookie = requests.utils.cookiejar_from_dict(json.load(f))
        s.cookies = cookie
    url = 'https://strefadb.pl/odcinki/' + nazwaSerii + '.html'
    k = s.get(url)
    result = k.text
    test = client.parseDOM(result, 'ul', attrs={'class':'lista-odcinkow'})
    test = client.parseDOM(test, 'li')
    lista = []
    lista_tytulow = []
    lista_linkow = []
    ocena = []
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
        addDir(str(i) + ' ' + str(lista_tytulow[i-1]), url, 10, '',obrazek,ocena[i-1], True)
        i+=1

################################Lektor###########################
if mode == 5 or 6:
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')

if name == 'Dragon Ball' and mode == 5:
    list_episodes('dragon-ball', 'lektor', resourcesPath + "db_art.jpg")

if name == 'Dragon Ball Z' and mode == 5:
    list_episodes('dragon-ball-z', 'lektor', resourcesPath + "dbz_art.jpg")

if name == 'Dragon Ball Kai' and mode == 5:
    list_episodes('dragon-ball-kai', 'lektor', resourcesPath + "dbkai_art.jpeg")

if name == 'Dragon Ball GT' and mode == 5:
    list_episodes('dragon-ball-gt', 'lektor', resourcesPath + "dbgt_art.png")

if name == 'Dragon Ball Super' and mode == 5:
    list_episodes('dragonball-super', 'lektor', resourcesPath + "dbs_art.jpg")

if name == 'Dragon Ball Heroes' and mode == 5:
    list_episodes('dragon-ball-heroes', 'lektor', resourcesPath + "dbh_art.jpg")

if name == 'Kinowki' and mode == 5:
    url = 'https://strefadb.pl/filmy-kinowe.html'
    result = client.request(url)
    test = client.parseDOM(result, 'ul', attrs={'class':'lista-odcinkow'})
    test = client.parseDOM(test, 'li')
    lista = []
    lista_tytulow = []
    lista_linkow = []
    for item in test:
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
        addDir(str(i) + ' ' + str(lista_tytulow[i-1]).replace('(', '| ocena odcinka: ('), url, 10, '',resourcesPath + "kino_fanart.jpg",'', True)
        i+=1

################################Napisy##################

if name == 'Dragon Ball' and mode == 6:
    list_episodes('dragon-ball', 'napisy', resourcesPath + "db_art.jpg")

if name == 'Dragon Ball Z' and mode == 6:
    list_episodes('dragon-ball-z', 'napisy', resourcesPath + "dbz_art.jpg")

if name == 'Dragon Ball Kai' and mode == 6:
    list_episodes('dragon-ball-kai', 'napisy', resourcesPath + "dbkai_art.jpeg")

if name == 'Dragon Ball GT' and mode == 6:
    list_episodes('dragon-ball-gt', 'napisy', resourcesPath + "dbgt_art.png")
        
if name == 'Dragon Ball Super' and mode == 6:
    list_episodes('dragonball-super', 'napisy', resourcesPath + "dbs_art.jpg")

if name == 'Dragon Ball Heroes' and mode == 6:
    list_episodes('dragon-ball-heroes', 'napisy', resourcesPath + "dbh_art.jpg")

if name == 'Kinowki' and mode == 6:
    url = 'https://strefadb.pl/filmy-kinowe.html'
    result = client.request(url)
    test = client.parseDOM(result, 'ul', attrs={'class':'lista-odcinkow'})
    test = client.parseDOM(test, 'li')
    lista = []
    lista_tytulow = []
    lista_linkow = []
    for item in test:
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
        addDir(str(i) + ' ' + str(lista_tytulow[i-1]).replace('(', '| ocena odcinka: ('), url, 10, '',resourcesPath + "kino_fanart.jpg",'', True)
        i+=1

###################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#

if mode == None or url == None or len(url) < 1 :
    if xbmcplugin.getSetting(int(sys.argv[1]), 'user') == '':
        dialog = xbmcgui.Dialog()
        dialog.ok('Blad!', 'Wpisz dane do logowania w ustawieniach :)')
        sys.exit(0)
    else:
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0' }
        data ={"login" : str(xbmcplugin.getSetting(int(sys.argv[1]), 'user')), 'password': str(xbmcplugin.getSetting(int(sys.argv[1]), 'pass')),'signin': 'ok'}
        s.post('https://strefadb.pl/', data=data, headers=headers)
        import json
        basePath = "special://temp/cookie.txt"
        path = xbmc.translatePath(basePath)
        with open(path, 'w') as f:
            json.dump(requests.utils.dict_from_cookiejar(s.cookies), f)
    CATEGORIES()

elif mode == 1 :
    mySearch()

elif mode == 2 :
    myOther()

elif mode == 3 :
    SUBCATEGORIES(3)

elif mode == 4 : 
    SUBCATEGORIES(4)

elif mode == 10 :
    basePath = "special://temp/cookie.txt"
    path = xbmc.translatePath(basePath)
    with open(path, 'r') as f:
        cookie = requests.utils.cookiejar_from_dict(json.load(f))
        s.cookies = cookie
    link = urllib.unquote_plus(params['url'])
    k = s.get(link)
    result = k.text
    result = client.parseDOM(result, 'iframe', ret='src')
    url = result[0]
    addDir("Mirror 1", url, 11, "","","", False)
    try:
        link = link + "&mirror=2"
        k = s.get(link)
        result = k.text
        result = client.parseDOM(result, 'iframe', ret='src')
        url = result[0]
        addDir("Mirror 2", url, 11, "","","", False)
    except:
        pass

elif mode == 11 :
    url = urllib.unquote_plus(params['url'])
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))

###################################################################################

xbmcplugin.endOfDirectory(int(sys.argv[1]))