# -*- coding: UTF-8 -*-
import sys
from HTMLParser import HTMLParser

import xbmc
import xbmcaddon
import xbmcplugin

from ptw.libraries import addon_utils as addon
from ptw.libraries import source_utils, client

reload(sys)
sys.setdefaultencoding('utf8')

__addon_id__ = 'plugin.video.dokumentalne.net'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id='plugin.video.dokumentalne.net')

url = ""

# =########################################################################################################=#
#                                                   MENU                                                   #
# =########################################################################################################=#

def CATEGORIES():
    addon.addDir("Szukaj", '', mode=1)
    addon.addDir("Kategorie", "", mode=20)
    addon.addDir("Najnowsze filmy", 'https://dokumentalne.net/najnowsze-filmy/', mode=10)
    addon.addDir("Filmy w HD", 'https://dokumentalne.net/category/hd-filmy/', mode=10)
    addon.addDir("Wszystkie filmy", 'https://dokumentalne.net/category/wszystkie-filmy/', mode=10)


###################################################################################
# =########################################################################################################=#
#                                                 FUNCTIONS                                                #
# =########################################################################################################=#

def mySearch():
    keyb = xbmc.Keyboard('', "Wyszukiwarka")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
        search = keyb.getText()
        link = "https://dokumentalne.net/?s=" + search
        ListujFilmy(link)
    else:
        CATEGORIES()


def ListujKategorie():
    kategorie = {"Astronomiczne": "https://dokumentalne.net/category/astronomiczne-kosmos/",
                 "Biograficzne": "https://dokumentalne.net/category/biograficzne/",
                 "Filmy HD": "https://dokumentalne.net/category/hd-filmy/",
                 "Historyczne": "https://dokumentalne.net/category/historyczne/",
                 "Katastroficzne": "https://dokumentalne.net/category/katastroficzne/",
                 "Kryminalne": "https://dokumentalne.net/category/kryminalne/",
                 "Motoryzacyjne": "https://dokumentalne.net/category/motoryzacyjne/",
                 "Naukowe": "https://dokumentalne.net/category/naukowe/",
                 "Podróżnicze": "https://dokumentalne.net/category/podroznicze/",
                 "Przyrodnicze": "https://dokumentalne.net/category/przyrodnicze/",
                 "Psychologiczne": "https://dokumentalne.net/category/psychologiczne/",
                 "Spoleczeństwo": "https://dokumentalne.net/category/spoleczenstwo/",
                 "Technologia": "https://dokumentalne.net/category/technologia/",
                 "Wojenne": "https://dokumentalne.net/category/wojenne/"
                 }
    for item in kategorie:
        addon.addDir(str(item), str(kategorie[item]), mode=10)


def ListujFilmy(url=""):
    try:
        url = params['url']
    except:
        pass
    result = client.request(url)
    h = HTMLParser()
    result = h.unescape(result)
    try:
        nawigacja = client.parseDOM(result, 'div', attrs={'class': 'wp-pagenavi'})
        nastepna = client.parseDOM(nawigacja, 'a', ret='href')[-2]
        nawigacja = client.parseDOM(nawigacja, 'a', attrs={'class': 'nextpostslink'})
    except:
        nawigacja = ""
    result = client.parseDOM(result, 'div', attrs={'class': 'entry-content'})

    for item in result:
        item2 = client.parseDOM(item, 'div', attrs={'class': 'picture-content '})
        if len(item2) == 0:
            continue
        opis = client.parseDOM(item, 'div', attrs={'class': 'excerpt sub-lineheight'})[0]
        link = client.parseDOM(item2, 'a', ret='href')[0]
        nazwa = client.parseDOM(item2, 'a', ret='title')[0]
        obraz = client.parseDOM(item2, 'img', ret='src')[0]
        addon.addLink(str(nazwa), str(link), mode=6, thumb=str(obraz), icon=str(obraz), plot=str(opis))
    if len(nawigacja) > 0:
        addon.addDir("Nastepna strona", str(nastepna), mode=10)


def ListujLinki():
    import resolveurl
    url = params['url']
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
        url = client.parseDOM(result, 'source', ret='src')[0]
        if str(url).startswith("//"):
            url = url.replace("//", "http://")
    except:
        url = client.parseDOM(result, 'iframe', ret='src')[0]
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

###############################################################################################################
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
