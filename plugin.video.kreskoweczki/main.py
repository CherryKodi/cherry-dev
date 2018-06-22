# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests,json
from resources.lib.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys
from HTMLParser import HTMLParser
from pipes import SOURCE

reload(sys)
sys.setdefaultencoding('utf8')
BASE_URL = "https://www.kreskoweczki.pl/"

pluginName=sys.argv[0].replace('plugin://','')
basePath = "special://home/addons/"+pluginName+"resources/media/"
resourcesPath = xbmc.translatePath(basePath)
default_background = resourcesPath + "default.jpg"

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#
def CATEGORIES():
    addDir("Szukaj", '', 1, '',resourcesPath + "search.png",default_background,'','','')
    addDir("Anime", "https://www.kreskoweczki.pl/typ/anime", 10, '',resourcesPath + "a.png",default_background,'','','')
    addDir("Bajki", 'https://www.kreskoweczki.pl/typ/bajka/strona-2', 10, '',resourcesPath + "b.png",default_background,'','','')
    addDir("Seriale", 'https://www.kreskoweczki.pl/typ/serial', 10, '',resourcesPath + "s.png",default_background,'','','')
    addDir("Pozostałe", 'https://www.kreskoweczki.pl/typ/pozostale', 10, '',resourcesPath + "p.png",default_background,'','','')
    addDir("Rankingi", '', 20, '',resourcesPath + "ranking.png",default_background,'','','')

###################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#

def mySearch():
    keyb = xbmc.Keyboard('', "Wyszukiwarka")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0 :
        search = keyb.getText()
        myParam = str(urllib.quote(search)).strip()
        link = "https://www.kreskoweczki.pl/szukaj?query="+search
        ListujSerie(link)
    else:
        CATEGORIES()

def addDir(name, url, mode, banner, thumb, fanart, opis, gatunek, rating, isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, banner, thumbnailImage=thumb)
    liz.setArt({
                'icon': thumb,
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

def ListujSerie(url = ""):
    try:
        url = urllib.unquote_plus(params['url'])
    except:
        pass
    if "bajka" in url:
        strona = int(url.split("-")[1]) + 1
        nawigacja2 = url.split("-")[0] + "-" + str(strona)
    else:
        nawigacja2 = ''
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    
    try:
        nawigacja = client.parseDOM(result, 'div', attrs={'class':'pagination pagination-centered'})
        nastepna = client.parseDOM(nawigacja, 'a')
        link_nastepna = client.parseDOM(nawigacja, 'a', ret='href')
        for item in zip(nastepna, link_nastepna):
            if "Następna »" in item[0]:
                nawigacja = str(item[1])
            else:
                nawigacja = ""
    except:
        nawigacja = ""

    result = client.parseDOM(result, 'ul', attrs={'class':'category-grid items-list miniature play'})
    linki = client.parseDOM(result, 'a', ret='href')
    ikony = re.findall("""style=\"background-image: url\('(.*?)'\)""", result[0])
    tytuly = client.parseDOM(result, 'b', attrs={'class':'larger white'})
    
    for item2 in zip(linki,ikony,tytuly):
        link = BASE_URL + str(item2[0]) + "/odcinki/1"
        ikona = BASE_URL + str(item2[1])
        tytul = str(item2[2])
        addDir(tytul, link, 11, "", ikona, default_background, "", "Anime", "")
    if len(nawigacja2) > 0:
        addDir("Nastepna strona", str(nawigacja2), 10, '','',default_background,'','','')
    if len(nawigacja) > 0:
        addDir("Nastepna strona", BASE_URL + str(nawigacja), 10, '','',default_background,'','','')

def ListujRanking(url = ""):
    try:
        url = urllib.unquote_plus(params['url'])
    except:
        pass
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    
    try:
        nawigacja = client.parseDOM(result, 'div', attrs={'class':'pagination pagination-centered'})
        nastepna = client.parseDOM(nawigacja, 'a')
        link_nastepna = client.parseDOM(nawigacja, 'a', ret='href')
        for item in zip(nastepna, link_nastepna):
            if "Następna »" in item[0]:
                nawigacja = str(item[1])
            else:
                nawigacja = ""
    except:
        nawigacja = ""

    result = client.parseDOM(result, 'ul', attrs={'class':'item-list'})
    linki = client.parseDOM(result, 'a', ret='href')
    ikony = re.findall("""style=\"background-image: url\('(.*?)'\)""", result[0])
    tytuly = client.parseDOM(result, 'b', attrs={'class':'larger white'})
    
    for item2 in zip(linki,ikony,tytuly):
        link = BASE_URL + str(item2[0]) + "/odcinki/1"
        ikona = BASE_URL + str(item2[1])
        tytul = str(item2[2])
        addDir(tytul, link, 11, "", ikona, "", "", "Anime", "")
    if len(nawigacja) > 0:
        addDir("Nastepna strona", BASE_URL + str(nawigacja), 10, '','',default_background,'','','')


def ListujOdcinki(url = ""):
    try:
        url = urllib.unquote_plus(params['url'])
    except:
        pass
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    nawigacja2 = ''
    strona = url.split("/")[-1]
    try:
        nawigacja = client.parseDOM(result, 'div', attrs={'class':'pagination pagination-centered'})
        nastepna = client.parseDOM(nawigacja, 'a')
        link_nastepna = client.parseDOM(nawigacja, 'a', ret='href')
        for item in zip(nastepna, link_nastepna):
            if "Następna »" in item[0]:
                nawigacja = str(item[1])
            else:
                nawigacja = ""
            if "Ostatnia »" in item[0]:
                nawigacja2 = str(item[1])
            else:
                nawigacja2 = ""
    except:
        nawigacja = ""

    result = client.parseDOM(result, 'ul', attrs={'class':'item-list'})
    result2 = client.parseDOM(result, 'li')
    linki = client.parseDOM(result, 'a', ret='href')
    ikony = re.findall("""style=\"background-image: url\('(.*?)'\)""", result[0])
    
    for item2 in zip(linki,ikony,result2):
        odcinek = client.parseDOM(item2[2], 'div', attrs={'class':'category-name fs16'})[1]
        odcinek = client.parseDOM(odcinek, 'span', attrs={'class':'white'})[0]
        link = BASE_URL + str(item2[0])
        ikona = BASE_URL + str(item2[1])
        tytul = str(odcinek)
        addDir(tytul, link, 12, "", ikona, "", "", "Anime", "")
    if len(nawigacja) > 0:
        addDir("Nastepna strona", BASE_URL + str(nawigacja), 11, '','',default_background,'','','')
    if len(nawigacja) == 0 and len(nawigacja2) > 0:
        ostatnia = nawigacja2.split("/")[-1]
        nowa = int(strona) + 1
        addDir("Nastepna strona", BASE_URL + str(nawigacja2).replace("/"+ostatnia,"/"+str(nowa)), 11, '','',default_background,'','','')

def ListujLinki():
    try:
        url = urllib.unquote_plus(params['url'])
    except:
        pass
    id = url.split("/")[5]
    s = requests.session()
    referer = "https://www.kreskoweczki.pl/fullscreen/"+id
    headers = {
        'Referer':referer,
        'User-Agent':"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3424.0 Safari/537.36",
        }
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    source_id = client.parseDOM(result, 'form', attrs={'action':'/fullscreen/'+id})
    source_id = client.parseDOM(source_id, 'input', ret='value')
    
    hostDict = resolveurl.relevant_resolvers(order_matters=True)
    hostDict = [i.domains for i in hostDict if not '*' in i.domains]
    hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
    hostDict = [x for y,x in enumerate(hostDict) if x not in hostDict[:y]]
    

    for item in source_id:
        data = {'source_id':str(item)}
        content = s.post("https://www.kreskoweczki.pl/fullscreen/"+id,data = data).content
        try:
            temp = client.parseDOM(content, 'div', attrs={'class':'playerholder'})
            video_link = client.parseDOM(temp, 'a', ret='href')[0]
        except:
            try:
                video_link = client.parseDOM(content, 'iframe', ret='src')[0]
            except:
                continue
        if str(video_link).startswith("//"):
            video_link = str(video_link).replace("//", "http://")
        valid, host = source_utils.is_host_valid(video_link, hostDict)
        if valid == False:
            continue
        else:
            nazwa = "[COLOR green]" + host + " [/COLOR]"
            addLink(nazwa, str(video_link), 6, "", "", default_background, "", "")

   
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
    
elif mode == 10 :
    ListujSerie()

elif mode == 11 :
    ListujOdcinki()
    
elif mode == 12 :
    ListujLinki()

elif mode == 20 :
    addDir("Ranking Ocen", 'https://www.kreskoweczki.pl/ranking/punkty', 21, '',resourcesPath + "oceny.png",default_background,'','','')
    addDir("Ranking Wyświetleń", 'https://www.kreskoweczki.pl/ranking/wyswietlenia', 21, '',resourcesPath + "wyswietlenia.png",default_background,'','','')

elif mode == 21 :
    url = urllib.unquote_plus(params['url'])
    ListujRanking()
    
elif mode == 6 : 
    url = urllib.unquote_plus(params['url'])
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
    
###################################################################################
xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))