# -*- coding: UTF-8 -*-
import json
import sys
import urllib

import requests
import xbmc
import xbmcgui
import xbmcplugin

reload(sys)
sys.setdefaultencoding('UTF8')

from ptw.libraries import addon_utils as addon
from ptw.libraries import client

try:
    import HTMLParser
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser

_pluginName = sys.argv[0].replace('plugin://', '')
_basePath = "special://home/addons/" + _pluginName + "resources/media/"
_resourcesPath = xbmc.translatePath(_basePath)
_default_background = _resourcesPath + "fanart.png"
_base_link = "https://shinden.pl/"


# =########################################################################################################=#
#                                                   MENU                                                   #
# =########################################################################################################=#

def CATEGORIES():
    addon.addDir("Szukaj po nazwie", '', mode=1, fanart=_default_background)
    addon.addDir("Filtruj", '', mode=2, fanart=_default_background)
    addon.addDir("Alfabetycznie", '', mode=10, fanart=_default_background)
    addon.addDir("Ranking najlepiej ocenianych",
                 'https://shinden.pl/titles?series_type%5B0%5D=TV&one_online=true&sort_by=ranking-rate&sort_order=desc',
                 mode=3, fanart=_default_background)


############################################################################################################
# =########################################################################################################=#
#                                                 FUNCTIONS                                                #
# =########################################################################################################=#

def Wyszukiwanie_Nazwa():
    keyb = xbmc.Keyboard('', "Wyszukiwarka anime")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
        search = keyb.getText()
        url = 'https://shinden.pl/titles?search=' + search + '&series_type%5B0%5D=TV&series_type%5B1%5D=Movie&series_type%5B2%5D=Special&series_status%5B0%5D=Proposal&series_status%5B1%5D=Currently+Airing&series_status%5B2%5D=Finished+Airing&one_online=true'
        data = {'url': url}
        r = requests.post("https://shinden.herokuapp.com/shinden", data=data).content
        h = HTMLParser()
        r = h.unescape(r)

        result = [item for item in client.parseDOM(r, 'li', attrs={'class': 'desc-col'}) if
                  str(item).startswith("<h3>")]
        obrazy = [_base_link + client.parseDOM(item, 'a', ret='href')[0] for item in
                  client.parseDOM(r, 'ul', attrs={'class': 'div-row'}) if '/res/images' in item]
        linki = [_base_link + item for item in client.parseDOM(result, 'a', ret='href') if
                 str(item).startswith("/titles")]
        nazwy = [client.parseDOM(item, 'a')[0] for item in result]
        oceny = client.parseDOM(r, 'li', attrs={'class': 'rate-top'})

        for item in zip(linki, nazwy, oceny, obrazy):
            try:
                title = str(item[1]).replace("<em>", '').replace("</em>", '')
                addon.addDir(title + " [COLOR ivory]([B]%s[/B])[/COLOR]" % str(item[2]), str(item[0]) + "/all-episodes",
                             thumb=str(item[3]), fanart=_default_background,
                             mode=4)
            except:
                continue
        try:
            strony = client.parseDOM(r, 'nav', attrs={'class': 'pagination'})
            strony = client.parseDOM(strony, 'li')
            link_nastepna = client.parseDOM(strony, 'a', ret='href')[-2]
            link_nastepna = urllib.unquote(link_nastepna).replace('amp;', '')
            if link_nastepna:
                addon.addDir("Następna strona...", _base_link + link_nastepna, mode=3, fanart=_default_background)
        except Exception as e:
            print(e)
            pass
    else:
        CATEGORIES()


def selectdialog():
    from resources.lib import selectdialog
    type = {'Wszystkie': '', 'TV': 'series_type[5]=TV', 'Film': 'series_type[1]=Movie', 'OVA': 'series_type[0]=OVA',
            'ONA': 'series_type[3]=ONA', 'Specjalne': 'series_type[2]=Special', 'Muzyczne': 'series_type[4]=Music'}
    sort = {'Ocena +': 'sort_by=ranking-rate&sort_order=desc', 'Ocena -': 'sort_by=ranking-rate&sort_order=asc',
            'Tytul +': 'https://shinden.pl/titles?sort_by=desc&sort_order=desc',
            'Tytul -': 'https://shinden.pl/titles?sort_by=desc&sort_order=asc'}
    genre_opt = {'Jeden z zaznaczonych': 'genres-type=one', 'Wszystkie z zaznaczonych': 'genres-type=all'}
    status = {'Wszystkie': '', 'Deklaracja': 'series_status[0]=Proposal', 'Zapowiedz': 'series_status[1]=Not yet aired',
              'Zakonczone': 'series_status[3]=Finished Airing', 'Emitowane': 'series_status[2]=Currently Airing'}
    genre = {5: u'Akcja', 106: u'Cyberpunk', 8: u'Dramat', 78: u'Ecchi', 1741: u'Eksperymentalne', 22: u'Fantasy',
             234: u'Hentai', 92: u'Historyczne', 51: u'Horror', 7: u'Komedia', 20: u'Kryminalne', 18: u'Magia',
             130: u'Harem', 98: u'Mecha', 263: u'Meski harem', 136: u'Muzyczne', 19: u'Nadprzyrodzone', 97: u'Obled',
             42: u'Okruchy zycia', 165: u'Parodia', 52: u'Psychologiczne', 38: u'Romans', 549: u'Sci-Fi',
             167: u'Shoujo-ai',
             207: u'Shounen-ai', 384: u'Space opera', 6: u'Przygodowe', 31: u'Sportowe', 1734: u'Steampunk',
             65: u'Szkolne', 57: u'Sztuki walki', 12: u'Tajemnica', 53: u'Thriller', 93: u'Wojskowe', 364: u'Yaoi',
             380: u'Yuri'}
    dialog = selectdialog.SelectDialog(title="Sortowanie", stype=type, sort=sort, status=status,
                                       genre=genre, genre_opt=genre_opt, callback=get_by_select)
    dialog.doModal()


def get_by_select(stype=[], sort=0, status=0, genre=[], genopt=[], offset=0):
    if offset:
        CATEGORIES()
    else:
        genre_string = ''
        if type(genre) is str:
            genre_string = str(genopt[0]) + "&genres=i" + str(genre)
        if type(genre) is list:
            genre_string = str(genopt[0]) + "&genres=" + ';'.join(str('i' + str(x)) for x in genre)

        type_string = ''
        if type(stype) is str:
            type_string = str(str(stype))
        if type(stype) is list:
            type_string = str('&'.join(str(x) for x in stype))

        url = "https://shinden.pl/titles?&"
        if genre_string:
            url += "%s&%s&%s&one_online=true&" % (sort, status, genre_string)
        else:
            url += "%s&%s&one_online=true&" % (sort, status)
        url += type_string
        data = {'url': url}
        r = requests.post("https://shinden.herokuapp.com/shinden", data=data).content
        h = HTMLParser()
        r = h.unescape(r)

        result = [item for item in client.parseDOM(r, 'li', attrs={'class': 'desc-col'}) if
                  str(item).startswith("<h3>")]
        obrazy = [_base_link + client.parseDOM(item, 'a', ret='href')[0] for item in
                  client.parseDOM(r, 'ul', attrs={'class': 'div-row'}) if '/res/images' in item]
        linki = [_base_link + item for item in client.parseDOM(result, 'a', ret='href') if
                 str(item).startswith("/titles")]
        nazwy = [client.parseDOM(item, 'a')[0] for item in result]
        oceny = client.parseDOM(r, 'li', attrs={'class': 'rate-top'})

        for item in zip(linki, nazwy, oceny, obrazy):
            try:
                title = str(item[1]).replace("<em>", '').replace("</em>", '')
                addon.addDir(title + " [COLOR ivory]([B]%s[/B])[/COLOR]" % str(item[2]), str(item[0]) + "/all-episodes",
                             thumb=str(item[3]),
                             mode=4, fanart=_default_background)
            except:
                continue
        try:
            strony = client.parseDOM(r, 'nav', attrs={'class': 'pagination'})
            strony = client.parseDOM(strony, 'li')
            link_nastepna = client.parseDOM(strony, 'a', ret='href')[-2]
            link_nastepna = urllib.unquote(link_nastepna).replace('amp;', '')
            if link_nastepna:
                addon.addDir("Następna strona...", _base_link + link_nastepna, mode=3, fanart=_default_background)
        except Exception as e:
            print(e)
            pass


def Alfabetycznie():
    url = "https://shinden.pl/titles"

    data = {'url': url}
    r = requests.post("https://shinden.herokuapp.com/shinden", data=data).content
    h = HTMLParser()
    r = h.unescape(r)

    result = client.parseDOM(r, 'ul', attrs={'id': 'TabLetters'})
    literki = client.parseDOM(result, 'a')
    literki_linki = client.parseDOM(result, 'a', ret='href')

    for item in zip(literki, literki_linki):
        try:
            addon.addDir(str(item[0]), str(url) + str(item[1]), fanart=_default_background, mode=3)
        except:
            continue


def ListowanieAnime():
    url = params['url']
    data = {'url': url}
    r = requests.post("https://shinden.herokuapp.com/shinden", data=data).content
    h = HTMLParser()
    r = h.unescape(r)

    result = [item for item in client.parseDOM(r, 'li', attrs={'class': 'desc-col'}) if str(item).startswith("<h3>")]
    obrazy = [_base_link + client.parseDOM(item, 'a', ret='href')[0] for item in
              client.parseDOM(r, 'ul', attrs={'class': 'div-row'}) if '/res/images' in item]
    linki = [_base_link + item for item in client.parseDOM(result, 'a', ret='href') if str(item).startswith("/titles")]
    nazwy = [client.parseDOM(item, 'a')[0] for item in result]
    oceny = client.parseDOM(r, 'li', attrs={'class': 'rate-top'})

    for item in zip(linki, nazwy, oceny, obrazy):
        try:
            addon.addDir(str(item[1]) + " [COLOR ivory]([B]%s[/B])[/COLOR]" % str(item[2]),
                         str(item[0]) + "/all-episodes", thumb=str(item[3]), mode=4, fanart=_default_background)
        except:
            continue
    try:
        strony = client.parseDOM(r, 'nav', attrs={'class': 'pagination'})
        strony = client.parseDOM(strony, 'li')
        link_nastepna = client.parseDOM(strony, 'a', ret='href')[-2]
        link_nastepna = urllib.unquote(link_nastepna).replace('amp;', '')
        if link_nastepna:
            addon.addDir("Następna strona...", _base_link + link_nastepna, mode=3, fanart=_default_background)
    except Exception as e:
        print(e)
        pass


def ListowaniOdcinkow():
    url = params['url'].replace('//titles', '/titles')
    data = {'url': url}
    result = requests.post("https://shinden.herokuapp.com/shinden", data=data).content
    h = HTMLParser()
    result = h.unescape(result)
    result = client.parseDOM(result, 'tbody', attrs={'class': 'list-episode-checkboxes'})
    result = client.parseDOM(result, 'tr')
    for item in result:
        try:
            item2 = client.parseDOM(item, 'td')[0]
            title = client.parseDOM(item, 'td', attrs={'class': 'ep-title'})[0]
            addon.addDir('Odcinek ' + str(item2) + ' ' + str(title),
                         _base_link + client.parseDOM(item, 'a', ret='href')[0], mode=5, fanart=_default_background)
        except:
            continue


def WysiwetlanieLinkow():
    url = params['url'].replace('//epek', '/epek')
    url = url.split('/epek/')
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.53 Safari/537.36"}
    filtered = json.loads(requests.get("https://shinden.herokuapp.com/epek/" + url[1], headers=headers).content)
    # filtered = json.loads(requests.get("http://127.0.0.1:5000/epek/" + url[1]).content)
    for i in filtered:
        try:
            if 'Polski' in i['audio']:
                addon.addLink("%s [COLOR ivory]([B]%s[/B])[/COLOR] - Polskie Audio" % (i['host'], i['quality']),
                              i['link'], mode=6,
                              fanart=_default_background)
            else:
                addon.addLink("%s [COLOR ivory]([B]%s[/B])[/COLOR] - %s" % (i['host'], i['quality'], i['napisy']),
                              i['link'], mode=6,
                              fanart=_default_background)
        except:
            continue


def OdpalanieLinku():
    url = params['url']
    if str(url).startswith("//"): url = "https://" + url
    url = url.split('/xhr/')
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.53 Safari/537.36"}
    url = url[1].replace('?', '/').replace(",", "=")

    thread = threading.Thread(target=Anulowanie)
    thread.start()
    video = requests.get("https://shinden.herokuapp.com/video/xhr/" + url, headers=headers).content
    global Zamknij
    Zamknij = False
    addon.PlayMedia(video)


import threading
from time import sleep

pDialog = xbmcgui.DialogProgress()
Zamknij = True


def Anulowanie():
    czas = 0
    pDialog.create('Informacja', 'Proszę czekać, trwa ładowanie!')
    while (Zamknij):
        czas += 0.05
        sleep(0.05)
        pDialog.update(int(float(100) / float(5.5 / czas)), "", "", "")
        try:
            if pDialog.iscanceled():
                pDialog.close()
                return
        except:
            pass
    pDialog.close()
    return


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
    Wyszukiwanie_Nazwa()

elif mode == 2:
    selectdialog()

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

###################################################################################

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]))
