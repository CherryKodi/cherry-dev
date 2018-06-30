# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests,time
from ptw.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys
reload(sys)
sys.setdefaultencoding('utf8')

## mode 1-9 funkcje strony
## mode 1 = szukajka
## mode 6 = play
## mode 10 = alfabet
## mode 20/30/40/50 kolejne kategorie

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
base_link = "http://www.animezone.pl/"

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#

def CATEGORIES():
    addDir("Szukaj anime", '', 1, '','','', True)
    addDir("Alfabetycznie", '', 10, '','','', True)
    addDir("Gatunki", '', 20, '','','', True)
    addDir("Sezony", '', 30, '','','', True)
    addDir("Rankingi", '', 40, '','','', True)

###################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#
def mySearch():
    keyb = xbmc.Keyboard('', "Wyszukiwarka anime")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0 :
        search = keyb.getText()
        myParam = str(urllib.quote(search)).strip()

        url = "http://www.animezone.pl/szukaj?q=" + search
        r = client.request(url)

        result2 = client.parseDOM(r, 'div', attrs={'class':'panel-body categories-newest'}) ## na obrazy
        obrazy = client.parseDOM(result2, 'img', ret='src')
        result = client.parseDOM(r, 'div', attrs={'class':'description pull-right'}) ## na linki i opisy
        linki = client.parseDOM(result, 'a', ret='href')
        nazwy = client.parseDOM(result, 'a')
        opisy = client.parseDOM(result, 'p')
        
        if len(linki) == 0:
            addDir("Zbyt dużo lub brak wyników wyszukiwania :(", '', None, 'ikona.png','thumb.png',None, True)
            addDir("Spróbuj doprecyzować zapytanie!", '', None, 'ikona.png','thumb.png',None, True)
        nazwy = client.parseDOM(result, 'a')
        
        counter = 0
        for link in linki:
            linki[counter] = 'http://animezone.pl' + linki[counter]
            obrazy[counter] = 'http://animezone.pl' + obrazy[counter]
            opisy[counter] = opisy[counter].replace("<mark>", "").replace("</mark>", "")
            addDir(str(nazwy[counter]).replace("<mark>", "").replace("</mark>", ""), linki[counter], 4, obrazy[counter],'',opisy[counter], True)
            counter+=1   
    else:
        CATEGORIES()
    
def myOther():
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('XBMC', 'Hello World')
    
def addDir(name, url, mode, iconimage, thumb, opis, isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)+'&iconimage='+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconimage, thumbnailImage=thumb)
    url = thumb
    liz.setArt({'thumb': thumb,
                'icon': iconimage,
                'fanart': url})
    liz.setInfo("Video", {'title':name , 'genre':'Anime', 'rating': 0, 'plot': opis})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def Alfabetycznie():
    url = 'http://animezone.pl'

    r = client.request('http://animezone.pl/anime/lista')

    result = client.parseDOM(r, 'div', attrs={'class':'btn-group btn-group-xs'})
    linki_litery = client.parseDOM(result, 'a', ret='href')
    litery = client.parseDOM(result, 'a')
    counter = 0
    for link in linki_litery:
        link = url + link
        addDir(str(litery[counter]), link, 3, '','','', True)
        counter+=1

def listowanieAnime():
    url = urllib.unquote_plus(params['url'])

    r = client.request(url)

    result2 = client.parseDOM(r, 'div', attrs={'class':'panel-body categories-newest'}) ## na obrazy
    obrazy = client.parseDOM(result2, 'img', ret='src')
    result = client.parseDOM(r, 'div', attrs={'class':'description pull-right'}) ## na linki i opisy
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a')
    opisy = client.parseDOM(result, 'p')
    
    counter = 0
    for link in linki:
        linki[counter] = 'http://animezone.pl' + linki[counter]
        obrazy[counter] = 'http://animezone.pl' + obrazy[counter]
        addDir(str(nazwy[counter]).replace("<mark>", "").replace("</mark>", ""), linki[counter], 4, obrazy[counter],'',opisy[counter], True)
        counter+=1   
    try:
        strony = client.parseDOM(r, 'ul', attrs={'class':'pagination'})
        strony = client.parseDOM(strony, 'li')
        link_nastepna = client.parseDOM(strony, 'a', ret='href')[-1]
        #nastepna strona
        for strona in strony:
            strona = client.parseDOM(strona, 'a')
            if len(strona) > 0:
                strona = str(strona[0])
                if strona == "&raquo;":
                    addDir("Nastpna strona..", 'http://animezone.pl' + link_nastepna, 3, 'ikona.png','thumb.png',None, True)
    except:
        print "blad"
        pass
        
def listowaniOdcinkow():
    url = urllib.unquote_plus(params['url'])
    try:
        iconimage= urllib.unquote_plus(params['iconimage'])
    except:
        iconimage = ''

    r = client.request(url)

    linki = []
    nazwy = []
    result = client.parseDOM(r, 'table', attrs={'class':'table table-bordered table-striped table-hover episodes'}) 
    test = client.parseDOM(result, 'tr')
    test = [x for x in test if str(x).startswith("<td class=\"text")]
    for item in test:
        link = client.parseDOM(item, 'a', ret='href')
        nazwa = client.parseDOM(item, 'td', attrs={'class':'episode-title'}) 
        odcinek = client.parseDOM(item, 'strong')[0]
        if nazwa and link:
            linki.append(link[0])
            nazwy.append("Odcinek " + odcinek + " " + nazwa[0])

    counter = 0
    for link in linki:
        linki[counter] = 'http://animezone.pl' + str(link).replace("..", "")
        addDir(str(nazwy[counter]), linki[counter], 5, iconimage,'thumb.png',None, True)
        counter += 1 

s = requests.session()

def wysiwetlanieLinkow():
    linki = []
    global url
    global nazwa
    url = urllib.unquote_plus(params['url'])
    r = s.get(url).content

    nazwa = urllib.unquote_plus(params['name'])
    results = client.parseDOM(r, 'table', attrs={'class':'table table-bordered table-striped table-hover episode'}) 
    results = client.parseDOM(results, 'td', attrs={'class':'text-center'})
    counter = range(-1,len(results)-1)
    for zipped in zip(counter,results):
        results.append(work(zipped))
    results = [x for x in results if type(x) == tuple]
    for result in results:
        addDir(result[0], result[1], 6, 'ikona.png','thumb.png',None, False)
    

def work(zipped):
    counter = zipped[0]
    result = zipped[1]
    counter += 1
    index = str(result).find('\" data')
    r = str(result)[index+12:]
    index = str(r).find(">")
    r = r[:index-1]
    if r.startswith("=\"spr"):
        return 0

    headers = {
    'Accept': '*/*',
    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.animezone.pl',
    'Referer': str(url).replace("http://", "http://www."),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
    }

    verify = s.get('http://animezone.pl/images/statistics.gif', headers = headers)

    hostDict = resolveurl.relevant_resolvers(order_matters=True)
    hostDict = [i.domains for i in hostDict if not '*' in i.domains]
    hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
    hostDict = [x for y,x in enumerate(hostDict) if x not in hostDict[:y]]
    #test
    
    
    headers = {
        'Host': 'www.animezone.pl',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept': '*/*',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': str(url).replace("http://", "http://www."),
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    
    data = {'data': r}
    response = s.post(str(url).replace("http://", "https://www."), headers = headers, data = data).content
    link = client.parseDOM(response, 'a', ret='href')

    try:
        if link == '':
            return 0
        if str(link[0]).startswith('//'):
            link[0] = str(link[0]).replace("//", "http://")
        valid, host = source_utils.is_host_valid(str(link[0]), hostDict)
        if valid == False:
            return 0
        else:
            nazwa2 = "[COLOR green]" + host + ": [/COLOR]" + nazwa
            return ("[B]" + str(nazwa2) + "[/B]",str(link[0]))
        return 0
        #addDir("[B]" + str(nazwa2) + "[/B]", str(link[0]), 6, 'ikona.png','thumb.png',None, False)
    except Exception, e:
        print e
        return 0

def rankingi(counter):
    url = urllib.unquote_plus(params['url'])

    r = client.request(url)

    result = client.parseDOM(r, 'table', attrs={'class':'table table-bordered table-striped table-hover ranking'})
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a')
    n=1
    try:
        for link in linki:
            linki[counter] = 'http://animezone.pl' + linki[counter]
            addDir(str(n) + ". " + str(nazwy[counter]).replace("<mark>", "").replace("</mark>", ""), linki[counter], 4, 'ikona.png','thumb.png',None, True)
            counter+=1
            n+=1
    except:
        pass

def gatunki(link,numer):
    url = 'http://www.animezone.pl/gatunki'

    r = client.request(url)

    result = client.parseDOM(r, 'form', attrs={'class':'species'})
    result = client.parseDOM(result, 'div', attrs={'class':'panel-body'})
    value = client.parseDOM(result[numer], 'input', ret='value')
    nazwa = client.parseDOM(result[numer], 'input')
    counter = 0
    for n in nazwa:
        index = str(n).find('  ')
        n = n[:index]
        nazwa[counter] = n
        addDir(str(nazwa[counter]), link + str(value[counter]), 3, '','','', True)
        counter+=1
def odpalanieLinku():
    url = urllib.unquote_plus(params['url'])
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
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

###################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#
if mode == None :
    CATEGORIES()
elif mode == 1 :
    mySearch()
elif mode == 2 :
    myOther()
elif mode == 3 :
    listowanieAnime()
elif mode == 4 :
    listowaniOdcinkow()
elif mode == 5 :
    wysiwetlanieLinkow()
elif mode == 6 : 
    odpalanieLinku()
elif mode == 10 :
    Alfabetycznie()
elif mode == 20 :
    addDir("Typ widowni", '', 21, '','','', True)
    addDir("Gatunek", '', 22, '','','', True)
    addDir("Tematyka", '', 23, '','','', True)
    addDir("Rok", '', 24, '','','', True)
elif mode == 21:
    gatunki('http://www.animezone.pl/gatunki?type=',0)
elif mode == 22:
    gatunki('http://www.animezone.pl/gatunki?species=',1)
elif mode == 23:
    gatunki('http://www.animezone.pl/gatunki?topic=',2)
elif mode == 24:
    gatunki('http://www.animezone.pl/gatunki?years=',3)
elif mode == 30 :
    counter = 1982
    while counter <=2018:
        addDir("Sezon Wiosna " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/wiosna', 3, '','','', True)
        addDir("Sezon Lato " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/lato', 3, '','','', True)
        addDir("Sezon Jesień " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/jesien', 3, '','','', True)
        addDir("Sezon Zima " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/zima', 3, '','','', True)
        counter+=1
elif mode == 40 :
    addDir("Ranking ocen", 'http://www.animezone.pl/anime/ranking/ocen', 41, '','','', True)
    addDir("Ranking wyświetleń", 'http://www.animezone.pl/anime/ranking/wyswietlen', 42, '','','', True)
    addDir("Ranking fanów", 'http://www.animezone.pl/anime/ranking/fanow', 42, '','','', True)
elif mode == 41 :
    rankingi(2)
elif mode == 42 :
    rankingi(1)
###################################################################################
xbmcplugin.endOfDirectory(int(sys.argv[1]))