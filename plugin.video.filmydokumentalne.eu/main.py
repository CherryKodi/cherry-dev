# -*- coding: UTF-8 -*-
import HTMLParser
import sys
import urllib
import xbmc
import xbmcplugin
from HTMLParser import HTMLParser

from ptw.libraries import addon_utils as addon
from ptw.libraries import source_utils, client

reload(sys)
sys.setdefaultencoding('utf8')

url = ""

# =########################################################################################################=#
#                                                   MENU                                                   #
# =########################################################################################################=#

def CATEGORIES():
    addon.addDir("Szukaj", '', mode=1)
    addon.addDir("Kanaly", "", mode=21)
    addon.addDir("Kategorie", "", mode=20)
    addon.addDir("Polecane", 'http://www.filmydokumentalne.eu/polecane/', mode=10)
    addon.addDir("Ranking", 'http://www.filmydokumentalne.eu/ranking/', mode=10)
    addon.addDir("Najnowsze", 'http://www.filmydokumentalne.eu/najnowsze-filmy/', mode=10)


###################################################################################
# =########################################################################################################=#
#                                                 FUNCTIONS                                                #
# =########################################################################################################=#

def mySearch():
    keyb = xbmc.Keyboard('', "Wyszukiwarka")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
        search = keyb.getText()
        link = "http://www.filmydokumentalne.eu/?s=" + search
        ListujFilmy(link)
    else:
        CATEGORIES()


def ListujKategorie():
    kategorie = {"Astrofizyka": "http://www.filmydokumentalne.eu/kategorie/astrofizyka/",
                 "Biograficzne": "http://www.filmydokumentalne.eu/kategorie/biograficzne/",
                 "Dusze czyśćcowe": "http://www.filmydokumentalne.eu/kategorie/dusze-czysccowe/",
                 "Ewangelizacyjne": "http://www.filmydokumentalne.eu/kategorie/ewangelizacyjne/",
                 "Ewolucja": "http://www.filmydokumentalne.eu/kategorie/ewolucja-kategorie/",
                 "Gadżeciarskie": "http://www.filmydokumentalne.eu/kategorie/gadzeciarskie/",
                 "Historyczne": "http://www.filmydokumentalne.eu/kategorie/historyczne/",
                 "II Wojna Światowa": "http://www.filmydokumentalne.eu/kategorie/ii-wojna-swiatowa-kategorie/",
                 "Katastroficzne": "http://www.filmydokumentalne.eu/kategorie/katastroficzne/",
                 "Kryminalne": "http://www.filmydokumentalne.eu/kategorie/kryminalne/",
                 "Kultura i sztuka": "http://www.filmydokumentalne.eu/kategorie/kultura-i-sztuka/",
                 "Lotnictwo": "http://www.filmydokumentalne.eu/kategorie/lotnictwo-kategorie/",
                 "Medycyna": "http://www.filmydokumentalne.eu/kategorie/medycyna/",
                 "Motoryzacja": "http://www.filmydokumentalne.eu/kategorie/motoryzacja-kategorie/",
                 "Nauka": "http://www.filmydokumentalne.eu/kategorie/nauka/",
                 "Obcojezyczne": "http://www.filmydokumentalne.eu/kategorie/obcojezyczne/",
                 "Paranormalne": "http://www.filmydokumentalne.eu/kategorie/paranormalne-2/",
                 "Podróżnicze": "http://www.filmydokumentalne.eu/kategorie/podroznicze/",
                 "Polityczne": "http://www.filmydokumentalne.eu/kategorie/polityczne/",
                 "Pozostale": "http://www.filmydokumentalne.eu/kategorie/pozostale/",
                 "Przetrwanie": "http://www.filmydokumentalne.eu/kategorie/przetrwanie-kategorie/",
                 "Przyrodnicze": "http://www.filmydokumentalne.eu/kategorie/przyrodnicze/",
                 "Religijne": "http://www.filmydokumentalne.eu/kategorie/religijne/",
                 "Sport": "http://www.filmydokumentalne.eu/kategorie/sport/",
                 "Spoleczenstwo": "http://www.filmydokumentalne.eu/kategorie/spoleczenstwo/",
                 "Technika": "http://www.filmydokumentalne.eu/kategorie/technika/",
                 "Wojskowe": "http://www.filmydokumentalne.eu/kategorie/wojskowe/",
                 }
    for item in kategorie:
        addon.addDir(str(item), str(kategorie[item]), mode=10)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)


def ListujKanaly():
    kanaly = {"Animal Planet": "http://www.filmydokumentalne.eu/kanaly/animal-planet/",
              "BBC": "http://www.filmydokumentalne.eu/kanaly/bbc/",
              "Canal+": "http://www.filmydokumentalne.eu/kanaly/canal/",
              "DC": "http://www.filmydokumentalne.eu/kanaly/dc/",
              "FokusTV": "http://www.filmydokumentalne.eu/kanaly/fokustv/",
              "HBO": "http://www.filmydokumentalne.eu/kanaly/hbo/",
              "History Channel": "http://www.filmydokumentalne.eu/kanaly/history-channel/",
              "NG": "http://www.filmydokumentalne.eu/kanaly/ng-kanaly/",
              "Planete": "http://www.filmydokumentalne.eu/kanaly/planete/",
              "Polsat": "http://www.filmydokumentalne.eu/kanaly/polsat/",
              "Polsat Play": "http://www.filmydokumentalne.eu/kanaly/polsat-play/",
              "Pozostale": "http://www.filmydokumentalne.eu/kanaly/pozostale-kanaly/",
              "TVN": "http://www.filmydokumentalne.eu/kanaly/tvn/",
              "TVP": "http://www.filmydokumentalne.eu/kanaly/tvp/",
              }
    for item in kanaly:
        addon.addDir(str(item), str(kanaly[item]), mode=10)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)


def ListujFilmy(url=""):
    try:
        url = urllib.unquote_plus(params['url'])
    except:
        pass
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    try:
        nawigacja = client.parseDOM(result, 'div', attrs={'class': 'wp-pagenavi'})
        nastepna = client.parseDOM(nawigacja, 'a', ret='href')[-1]
        nawigacja = client.parseDOM(nawigacja, 'a', attrs={'class': 'nextpostslink'})
    except:
        nawigacja = ""
    result = client.parseDOM(result, 'div', attrs={'id': 'left'})
    result = client.parseDOM(result, 'div', attrs={'id': 'news'})
    for item in result:
        link = client.parseDOM(item, 'a', ret='href')[0]
        nazwa = client.parseDOM(item, 'a')[0]
        addon.addLink(str(nazwa).replace("„", "").replace('”', ''), str(link), mode=6)
    if len(nawigacja) > 0:
        addon.addDir("Nastepna strona", str(nastepna), mode=10)


def ListujLinki():
    import resolveurl
    url = urllib.unquote_plus(params['url'])
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    result = client.parseDOM(result, 'table', attrs={'class': 'table table-bordered'})
    linki = client.parseDOM(result, 'a', ret='href')
    for item in linki:
        temp = client.request(str(item))
        link = client.parseDOM(temp, 'iframe', ret='src')[0]
        hostDict = resolveurl.relevant_resolvers(order_matters=True)
        hostDict = [i.domains for i in hostDict if not '*' in i.domains]
        hostDict = [i.lower() for i in reduce(lambda x, y: x + y, hostDict)]
        hostDict = [x for y, x in enumerate(hostDict) if x not in hostDict[:y]]
        valid, host = source_utils.is_host_valid(str(link), hostDict)
        if valid == False:
            continue
        addon.addLink("[B]" + host + "[/B]", link, mode=6)


def WyciaganieLinku():
    url = params['url']
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
    return url


###################################################################################
# =########################################################################################################=#
#                                               GET PARAMS                                                 #
# =########################################################################################################=#

params = addon.get_params()
url = params.get('url')
name = params.get('name')
try:
    mode = int(params.get('mode'))
except:
    mode = None
iconimage = params.get('iconimage')

###################################################################################
# =###########################################################################################################=#
#                                                   MODES                                                     #
# =###########################################################################################################=#

if mode == None:
    CATEGORIES()
elif mode == 1:
    mySearch()

#####MENU######
elif mode == 20:
    ListujKategorie()
elif mode == 21:
    ListujKanaly()
elif mode == 10:
    ListujFilmy()
elif mode == 11:
    ListujLinki()

elif mode == 6:
    url = WyciaganieLinku()
    addon.PlayMedia(url)

###################################################################################
xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))
