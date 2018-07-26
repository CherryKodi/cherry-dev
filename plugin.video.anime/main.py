# -*- coding: UTF-8 -*-
import re
import urllib
import xbmc
import xbmcplugin

import requests
import resolveurl
import sys

from ptw.debug import log_exception
from ptw.libraries import addon_utils as addon
from ptw.libraries import source_utils, client

_pluginName = sys.argv[0].replace('plugin://', '')
_basePath = "special://home/addons/" + _pluginName + "resources/media/"
_resourcesPath = xbmc.translatePath(_basePath)
_default_background = _resourcesPath + "fanart.jpg"
_base_link = "http://www.animezone.pl/"

s = requests.session()


# =########################################################################################################=#
#                                                   MENU                                                   #
# =########################################################################################################=#

def CATEGORIES():
    addon.addDir("Szukaj anime", '', mode=1)
    addon.addDir("Alfabetycznie", '', mode=10)
    addon.addDir("Gatunki", '', mode=20)
    addon.addDir("Sezony", '', mode=30)
    addon.addDir("Rankingi", '', mode=40)


############################################################################################################
# =########################################################################################################=#
#                                                 FUNCTIONS                                                #
# =########################################################################################################=#

def Wyszukiwanie():
    keyb = xbmc.Keyboard('', "Wyszukiwarka anime")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
        search = keyb.getText()

        url = "http://www.animezone.pl/szukaj?q=" + search
        r = client.request(url)

        result2 = client.parseDOM(r, 'div', attrs={'class': 'panel-body categories-newest'})  ## na obrazy
        obrazy = client.parseDOM(result2, 'img', ret='src')
        result = client.parseDOM(r, 'div', attrs={'class': 'description pull-right'})  ## na linki i opisy
        linki = client.parseDOM(result, 'a', ret='href')
        nazwy = client.parseDOM(result, 'a')
        opisy = client.parseDOM(result, 'p')

        if len(linki) == 0:
            addon.addDir("Zbyt dużo lub brak wyników wyszukiwania :(", '')
            addon.addDir("Spróbuj doprecyzować zapytanie!", '')
        nazwy = client.parseDOM(result, 'a')

        counter = 0
        for link in linki:
            linki[counter] = 'http://animezone.pl' + linki[counter]
            obrazy[counter] = 'http://animezone.pl' + obrazy[counter]
            opisy[counter] = opisy[counter].replace("<mark>", "").replace("</mark>", "")
            addon.addDir(str(nazwy[counter]).replace("<mark>", "").replace("</mark>", ""), linki[counter], mode=4,
                         thumb=obrazy[counter], plot=opisy[counter])
            counter += 1
    else:
        CATEGORIES()


def Alfabetycznie():
    url = 'http://animezone.pl'

    r = client.request('http://animezone.pl/anime/lista')

    result = client.parseDOM(r, 'div', attrs={'class': 'btn-group btn-group-xs'})
    linki_litery = client.parseDOM(result, 'a', ret='href')
    litery = client.parseDOM(result, 'a')
    counter = 0
    for link in linki_litery:
        link = url + link
        addon.addDir(str(litery[counter]), link, mode=3)
        counter += 1


def ListowanieAnime():
    url = params['url']

    r = client.request(url)

    result2 = client.parseDOM(r, 'div', attrs={'class': 'panel-body categories-newest'})  ## na obrazy
    obrazy = client.parseDOM(result2, 'img', ret='src')
    result = client.parseDOM(r, 'div', attrs={'class': 'description pull-right'})  ## na linki i opisy
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a')
    opisy = client.parseDOM(result, 'p')

    counter = 0
    for link in linki:
        linki[counter] = 'http://animezone.pl' + linki[counter]
        obrazy[counter] = 'http://animezone.pl' + obrazy[counter]
        addon.addDir(str(nazwy[counter]).replace("<mark>", "").replace("</mark>", ""), linki[counter], mode=4,
                     thumb=obrazy[counter], plot=opisy[counter])
        counter += 1
    try:
        strony = client.parseDOM(r, 'ul', attrs={'class': 'pagination'})
        strony = client.parseDOM(strony, 'li')
        link_nastepna = client.parseDOM(strony, 'a', ret='href')[-1]
        # nastepna strona
        for strona in strony:
            strona = client.parseDOM(strona, 'a')
            if len(strona) > 0:
                strona = str(strona[0])
                if strona == "&raquo;":
                    addon.addDir("Nastpna strona..", 'http://animezone.pl' + link_nastepna, mode=3)
    except:
        log_exception()
        pass


def ListowaniOdcinkow():
    url = params['url']

    try:
        iconimage = params['iconimage']
    except:
        iconimage = ''

    r = client.request(url)

    linki = []
    nazwy = []

    result = client.parseDOM(r, 'table', attrs={'class': 'table table-bordered table-striped table-hover episodes'})
    test = client.parseDOM(result, 'tr')
    test = [x for x in test if str(x).startswith("<td class=\"text")]
    for item in test:
        link = client.parseDOM(item, 'a', ret='href')
        nazwa = client.parseDOM(item, 'td', attrs={'class': 'episode-title'})
        odcinek = client.parseDOM(item, 'strong')[0]
        if nazwa and link:
            linki.append(link[0])
            nazwy.append("Odcinek " + odcinek + " " + nazwa[0])

    counter = 0
    for link in linki:
        linki[counter] = 'http://animezone.pl' + str(link).replace("..", "")
        addon.addDir(str(nazwy[counter]), linki[counter], mode=5, icon=iconimage)
        counter += 1


def WysiwetlanieLinkow():
    global url
    global nazwa

    url = params['url']
    r = s.get(url).content

    nazwa = params['name']
    results = client.parseDOM(r, 'table', attrs={'class': 'table table-bordered table-striped table-hover episode'})
    results = client.parseDOM(results, 'td', attrs={'class': 'text-center'})
    counter = range(-1, len(results) - 1)
    for zipped in zip(counter, results):
        results.append(work(zipped))
    results = [x for x in results if type(x) == tuple]
    for result in results:
        addon.addLink(result[0], result[1], mode=6)


def work(zipped):
    counter = zipped[0]
    result = zipped[1]
    counter += 1

    try:
        r = re.findall("""data-.*="([0-9].*)">""", result)[0]
    except:
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

    verify = s.get('http://animezone.pl/images/statistics.gif', headers=headers)

    hostDict = resolveurl.relevant_resolvers(order_matters=True)
    hostDict = [i.domains for i in hostDict if not '*' in i.domains]
    hostDict = [i.lower() for i in reduce(lambda x, y: x + y, hostDict)]
    hostDict = [x for y, x in enumerate(hostDict) if x not in hostDict[:y]]

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
    response = s.post(str(url).replace("http://", "https://www."), headers=headers, data=data).content
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
            return ("[B]" + str(nazwa2) + "[/B]", str(link[0]))
    except:
        log_exception()
        return 0


def Rankingi(counter):
    url = params['url']
    r = client.request(url)

    result = client.parseDOM(r, 'table', attrs={'class': 'table table-bordered table-striped table-hover ranking'})
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a')
    n = 1
    try:
        for link in linki:
            linki[counter] = 'http://animezone.pl' + linki[counter]
            addon.addDir(str(n) + ". " + str(nazwy[counter]).replace("<mark>", "").replace("</mark>", ""),
                         linki[counter], mode=4)
            counter += 1
            n += 1
    except:
        log_exception()
        pass


def Gatunki(link, numer):
    try:
        url = 'http://www.animezone.pl/gatunki'

        r = client.request(url)

        result = client.parseDOM(r, 'form', attrs={'class': 'species'})
        result = client.parseDOM(result, 'div', attrs={'class': 'panel-body'})
        value = client.parseDOM(result[numer], 'input', ret='value')
        nazwa = client.parseDOM(result[numer], 'input')
        counter = 0
        for n in nazwa:
            index = str(n).find('  ')
            n = n[:index]
            nazwa[counter] = n
            addon.addDir(str(nazwa[counter]), link + str(value[counter]), mode=3)
            counter += 1
    except:
        log_exception()


def OdpalanieLinku():
    url = params['url']
    addon.PlayMedia(url)


############################################################################################################
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
    Wyszukiwanie()

elif mode == 3:
    ListowanieAnime()

elif mode == 4:
    ListowaniOdcinkow()

elif mode == 5:
    WysiwetlanieLinkow()

elif mode == 6:
    OdpalanieLinku()

elif mode == 10:
    Alfabetycznie()

elif mode == 20:
    addon.addDir("Typ widowni", '', mode=21)
    addon.addDir("Gatunek", '', mode=22)
    addon.addDir("Tematyka", '', mode=23)
    addon.addDir("Rok", '', mode=24)

elif mode == 21:
    Gatunki('http://www.animezone.pl/gatunki?type=', 0)

elif mode == 22:
    Gatunki('http://www.animezone.pl/gatunki?species=', 1)

elif mode == 23:
    Gatunki('http://www.animezone.pl/gatunki?topic=', 2)

elif mode == 24:
    Gatunki('http://www.animezone.pl/gatunki?years=', 3)

elif mode == 30:
    counter = 1982
    while counter <= 2019:
        addon.addDir("Sezon Wiosna " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/wiosna',
                     mode=3)
        addon.addDir("Sezon Lato " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/lato',
                     mode=3)
        addon.addDir("Sezon Jesień " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/jesien',
                     mode=3)
        addon.addDir("Sezon Zima " + str(counter), 'http://www.animezone.pl/anime/sezony/' + str(counter) + '/zima',
                     mode=3)
        counter += 1

elif mode == 40:
    addon.addDir("Ranking ocen", 'http://www.animezone.pl/anime/ranking/ocen', mode=41)
    addon.addDir("Ranking wyświetleń", 'http://www.animezone.pl/anime/ranking/wyswietlen', mode=42)
    addon.addDir("Ranking fanów", 'http://www.animezone.pl/anime/ranking/fanow', mode=42)

elif mode == 41:
    Rankingi(2)

elif mode == 42:
    Rankingi(1)

###################################################################################

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))
