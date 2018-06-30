# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests
from resources.lib.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys

reload(sys)
sys.setdefaultencoding('utf8')

imdbsearch = "https://www.thetvdb.com/api/GetSeries.php?seriesname=%s&language=all"
banner_url = "https://www.thetvdb.com/banners/graphical/%s-g.jpg"
fanart_url = "https://www.thetvdb.com/banners/fanart/original/%s-1.jpg"
poster_url = "https://www.thetvdb.com/banners/posters/%s-1.jpg"

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#
def CATEGORIES():
    addDir("Szukaj kreskówki", '', 1, '','','',"","","")
    addDir("Alfabetycznie", '', 2, '','','',"","","")
    addDir("Rankingi", '', 10, '','','',"","","")

###################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#
def mySearch():
    keyb = xbmc.Keyboard('', "Wyszukiwarka kreskówek")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0 :
        search = keyb.getText()
        myParam = str(urllib.quote(search)).strip()
        url = "http://www.kreskowkazone.pl/szukaj?szukana=" + search
        r = client.request(url)
        result = client.parseDOM(r, 'div', attrs={'class':'box-img'})
        linki = client.parseDOM(result, 'a', ret='href')
        if len(linki) == 0:
            addDir("Zbyt dużo lub brak wyników wyszukiwania :(", '', None, 'ikona.png','thumb.png',"","","","")
            addDir("Spróbuj doprecyzować zapytanie!", '', None, 'ikona.png','thumb.png',"","","","")
        nazwy = client.parseDOM(result, 'a')
        nazwy = client.parseDOM(nazwy, 'img', ret='alt')
        
        counter = 0
        for link in linki:
            linki[counter] = 'http://www.kreskowkazone.pl/' + str(link)
            addDir(str(nazwy[counter]), linki[counter], 4, 'ikona.png','thumb.png',"","","","")
            counter+=1   
    else:
        CATEGORIES()
    
def myOther():
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('XBMC', 'Hello World')

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
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def Alfabetycznie():
    url = 'http://www.kreskowkazone.pl/'
    r = client.request('http://www.kreskowkazone.pl/lista_anime-0')
    result = client.parseDOM(r, 'li', attrs={'class':'litery'})
    linki_litery = client.parseDOM(result, 'a', ret='href')
    litery = client.parseDOM(result, 'a')
    counter = 0
    for link in linki_litery:
        link = url + link
        addDir(str(litery[counter]), link, 3, "", "", "", "", "", "")
        counter+=1

def Listowanie_Alfabetyczne():
    url = urllib.unquote_plus(params['url'])
    r = client.request(url)
    result = client.parseDOM(r, 'div', attrs={'class':'box-img'})
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a')
    nazwy = client.parseDOM(nazwy, 'img', ret='alt')
    
    counter = 0
    for link in linki:
        fanart,banner,thumb = Tvdb_Scraper(nazwy[counter])
        linki[counter] = 'http://www.kreskowkazone.pl/' + str(link)
        addDir(str(nazwy[counter]), linki[counter], 4, banner, thumb, fanart, "opis", "Kreskowka", "")
        counter+=1
        
def Listowanie_Ranking(id):
    url = urllib.unquote_plus(params['url'])
    r = client.request(url)
    result = client.parseDOM(r, 'table', attrs={'class':'tablesorter mytable3'})[id]
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a', ret='title')
    counter = 0
    for link in linki:
        fanart,banner,thumb = Tvdb_Scraper(nazwy[counter])
        linki[counter] = 'http://www.kreskowkazone.pl/' + str(link)
        addDir(str(nazwy[counter]).replace(" online", ""), linki[counter], 4, banner, thumb, fanart, "opis", "Kreskowka", "")
        counter+=1
        
def Tvdb_Scraper(nazwa):
    if xbmcplugin.getSetting(int(sys.argv[1]), 'tvdb') == "true":
        fanart = ""
        banner = ""
        thumb = ""
        try:
            temp_nazwa = str(nazwa).split(" (")[0]
            id = client.request(imdbsearch % temp_nazwa)
            id = re.findall("""<seriesid>(.*)</seriesid>""", id)[0]
            fanart = fanart_url % id
            banner = banner_url % id
            thumb = poster_url % id
        except Exception,e:
            id = ""
        return fanart,banner,thumb
    else:
        fanart = ""
        banner = ""
        thumb = ""
        return fanart,banner,thumb

s = requests.Session()

def Listowanie_Odcinkow():
    url = urllib.unquote_plus(params['url'])
    r = s.get(url).content
    result = client.parseDOM(r, 'td', attrs={'class':'border-c2'}) 
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a', ret='title')
    nazwy2 = []
    counter2 = 1
    while counter2 < len(result):
        if result[counter2+1] == '-':
            counter2+=4
            continue
        nazwy2.append(str(result[counter2-1]) + ". " + str(result[counter2]))
        counter2+=4
    ##cookies save
    import json
    basePath = "special://temp/cookie.txt"
    path = xbmc.translatePath(basePath)
    with open(path, 'w') as f:
        json.dump(requests.utils.dict_from_cookiejar(s.cookies), f)
    counter = 0
    for link in linki:
        linki[counter] = 'http://www.kreskowkazone.pl/' + str(link)
        addDir(str(nazwy2[counter]), linki[counter], 5, "banner.png", "thumb.png", "fanart.png", "opis", "gatunek", "")
        counter+=1
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def Wyciaganie_Linkow():
    test = []
    import json
    basePath = "special://temp/cookie.txt"
    path = xbmc.translatePath(basePath)
    with open(path, 'r') as f:
        cookie = requests.utils.cookiejar_from_dict(json.load(f))
        s.cookies = cookie
    url = urllib.unquote_plus(params['url'])
    r = s.get(url, cookies = s.cookies).content

    results = client.parseDOM(r, 'tr', attrs={'class':'wiersz'}) 
    counter = -1
    for result in results:
        counter+=1
        nazwa = client.parseDOM(result, 'a', ret='title')[0]
        index = str(result).find('\" rel')
        r = str(result)[index+10:]
        index = str(r).find("\"")
        r = r[:index]
        data ={"o" : str(r)}
        headers = {
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'http://www.kreskowkazone.pl/odcinki-online_101-dalmatynczykow-1997_28',
            'Connection': 'keep-alive',
            }

        s.get('http://www.kreskowkazone.pl/images/statystyki.gif', headers=headers, cookies = s.cookies)
        
        headers = {
        'Host': 'www.kreskowkazone.pl',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Referer': url,
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
        }
        hostDict = resolveurl.relevant_resolvers(order_matters=True)
        hostDict = [i.domains for i in hostDict if not '*' in i.domains]
        hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
        hostDict = [x for y,x in enumerate(hostDict) if x not in hostDict[:y]]
        response = s.post("http://www.kreskowkazone.pl/odcinki_emb", data = data, headers=headers, cookies = s.cookies)
        link = client.parseDOM(response.text, 'iframe', ret='src')
        try:
            if link == '':
                continue
            if str(link[0]).startswith('//'):
                link[0] = str(link[0]).replace("//", "http://")
            valid, host = source_utils.is_host_valid(str(link[0]), hostDict)
            if valid == False:
                continue
            nazwa = "[COLOR green]" + host + ": [/COLOR]" + nazwa
            addLink("[B]" + str(nazwa) + "[/B]", str(link[0]), 6, "", "", "", "", "")
        except:
            continue
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
elif mode == 2 :
    Alfabetycznie()
elif mode == 3 :
    Listowanie_Alfabetyczne()
elif mode == 4 :
    Listowanie_Odcinkow()
elif mode == 5 :
    Wyciaganie_Linkow()
elif mode == 6 : 
    url = urllib.unquote_plus(params['url'])
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
elif mode == 10 :
    ranking_url = "http://www.kreskowkazone.pl/ranking_anime"
    addDir("50 NAJCZĘŚCIEJ OGLĄDANYCH KRESKÓWEK", ranking_url, 11, "", "", "", "", "", "")
    addDir("50 NAJWYŻEJ OCENIANYCH KRESKÓWEK", ranking_url, 12, '','','',"","","")
    addDir("50 NAJCZĘŚCIEJ OGLĄDANYCH FILMÓW ANIMOWANYCH", ranking_url, 13, '','','',"","","")
    addDir("50 NAJWYŻEJ OCENIANYCH FILMÓW ANIMOWANYCH", ranking_url, 14, '','','',"","","")
    addDir("50 NAJCZĘŚCIEJ OGLĄDANYCH SERIALI", ranking_url, 15, '','','',"","","")
    addDir("50 NAJWYŻEJ OCENIANYCH SERIALI", ranking_url, 16, '','','',"","","")
elif mode == 11 :
    Listowanie_Ranking(0)
elif mode == 12 :
    Listowanie_Ranking(1)
elif mode == 13 :
    Listowanie_Ranking(2)
elif mode == 14 :
    Listowanie_Ranking(3)
elif mode == 15 :
    Listowanie_Ranking(4)
elif mode == 16 :
    Listowanie_Ranking(5)
###################################################################################
xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)