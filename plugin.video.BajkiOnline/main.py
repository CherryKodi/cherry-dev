# -*- coding: UTF-8 -*-
import HTMLParser
import urllib
import xbmcaddon
import xbmcplugin
import re
import sys
import threading

from HTMLParser import HTMLParser
from ptw.debug import log_exception
from ptw.libraries import addon_utils as addon
from ptw.libraries import source_utils, client

__addon_id__ = 'plugin.video.BajkiOnline'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id='plugin.video.BajkiOnline')

imdbsearch = "https://www.thetvdb.com/api/GetSeries.php?seriesname=%s&language=all"
banner_url = "https://www.thetvdb.com/banners/graphical/%s-g.jpg"
fanart_url = "https://www.thetvdb.com/banners/fanart/original/%s-1.jpg"
poster_url = "https://www.thetvdb.com/banners/posters/%s-1.jpg"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}


# =########################################################################################################=#
#                                                   MENU                                                   #
# =########################################################################################################=#

def HOME():
    addon.addDir("Bajki Alfabetycznie", "http://bajkionline.com/", mode=10)


############################################################################################################
# =########################################################################################################=#
#                                                 FUNCTIONS                                                #
# =########################################################################################################=#

def split_processing(items, num_splits=64):
    split_size = len(items)  # num_splits
    threads = []
    for i in range(num_splits):
        start = i * split_size
        end = None if i + 1 == num_splits else (i + 1) * split_size
        threads.append(
            threading.Thread(target=work, args=(items, start, end)))
        threads[-1].start()
    for t in threads:
        t.join()


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
        except:
            log_exception()
            id = ""
        return fanart, banner, thumb
    else:
        fanart = ""
        banner = ""
        thumb = ""
        return fanart, banner, thumb


def work(items, start, end):
    for item in items[start:end]:
        try:
            h = HTMLParser()
            item = h.unescape(item)
            link = str(client.parseDOM(item, 'a', ret='href')[0])
            title = str(client.parseDOM(item, 'a')[0])
            if title == "Gry": return
            try:
                plot = str(client.parseDOM(item, 'a', ret='title')[0])
            except:
                log_exception()
                plot = ""
            fanart, banner, thumb = Tvdb_Scraper(title)
            addon.addDir(title, link, mode=11, banner=banner, thumb=thumb, fanart=fanart, plot=plot, genre="Bajka")
        except Exception:
            log_exception()
            print('error with item')


def listowanieBajek():
    url = urllib.unquote_plus(params['url'])
    r = client.request(url)
    result = client.parseDOM(r, 'div', attrs={'id': 'categories-8'})
    result = client.parseDOM(result, 'li')
    split_processing(result)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)


def listowanieOdcinkow():
    try:
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
        url = urllib.unquote_plus(params['url'])
        r = client.request(url)
        result = client.parseDOM(r, 'div', attrs={'class': 'item-thumbnail'})
        for item in result:
            h = HTMLParser()
            item = h.unescape(item)
            link = str(client.parseDOM(item, 'a', ret='href')[0])
            title = str(client.parseDOM(item, 'a', ret='title')[0])
            thumb = str(client.parseDOM(item, 'img', ret='src')[0])
            addon.addLink(title, link, mode=12, thumb=thumb, icon=thumb, genre='Bajka')
    except:
        log_exception()
        return


def wyciaganieLinku():
    try:
        url = urllib.unquote_plus(params['url'])
        r = client.request(url)
        video_url = client.parseDOM(r, 'iframe', ret='src')[0]
        return video_url
    except:
        log_exception()
        return


def playVideo(url):
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
    HOME()
elif mode == 1:
    debug = 1
elif mode == 2:
    playVideo(url)
elif mode == 5:
    r = client.request(url)
elif mode == 10:
    listowanieBajek()
elif mode == 11:
    listowanieOdcinkow()
elif mode == 12:
    url = wyciaganieLinku()
    playVideo(url)

###############################################################################################################

xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
