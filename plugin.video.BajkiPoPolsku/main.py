# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests ,resolveurl, json, re
from resources.lib.libraries import source_utils, dom_parser, client, cleantitle
from HTMLParser import HTMLParser

import sys
reload(sys)
sys.setdefaultencoding('utf8')

__addon_id__= 'plugin.video.BajkiPoPolsku'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id='plugin.video.BajkiPoPolsku')

imdbsearch = "https://www.thetvdb.com/api/GetSeries.php?seriesname=%s&language=all"
banner_url = "https://www.thetvdb.com/banners/graphical/%s-g.jpg"
fanart_url = "https://www.thetvdb.com/banners/fanart/original/%s-1.jpg"
poster_url = "https://www.thetvdb.com/banners/posters/%s-1.jpg"

HEADERS = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#

def HOME():
    #ListowanieBajek()
    addDir("Bajki Alfabetycznie","http://bajkipopolsku.com/",10,"","","","","","")
    #addDir("Filmy","http://bajkipopolsku.com/category/fimly/page/",20,"","","","","","")

############################################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#

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

import threading

def split_processing(items, num_splits=64):                                      
    split_size = len(items) # num_splits                                       
    threads = []                                                                
    for i in range(num_splits):                                                 
        # determine the indices of the list this thread will handle             
        start = i * split_size                                                  
        # special case on the last chunk to account for uneven splits           
        end = None if i+1 == num_splits else (i+1) * split_size                 
        # create the thread                                                     
        threads.append(                                                         
            threading.Thread(target=work, args=(items, start, end)))         
        threads[-1].start() # start the thread we just created                  

    # wait for all threads to finish                                            
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
        except Exception,e:
            id = ""
        return fanart,banner,thumb
    else:
        fanart = ""
        banner = ""
        thumb = ""
        return fanart,banner,thumb

def work(items, start, end):
    for item in items[start:end]:
        try:
            h = HTMLParser()
            item = h.unescape(item)
            link = str(client.parseDOM(item, 'a', ret='href')[0])
            title = str(client.parseDOM(item, 'a')[0])
            if title == "Gry": continue
            try: 
                plot = str(client.parseDOM(item, 'a', ret='title')[0])
            except:
                plot = ""
            fanart,banner,thumb = Tvdb_Scraper(title)
            addDir(title, link, 11, banner, thumb, fanart, plot, "Bajka", "")
        except Exception:
            print('error with item') 

def ListowanieBajek():
    url = urllib.unquote_plus(params['url'])
    r = client.request(url)
    result = client.parseDOM(r, 'div', attrs={'id':'categories-4'})
    result = client.parseDOM(result, 'li')
    split_processing(result)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def ListowanieOdcinkow():
    try:
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
        url = urllib.unquote_plus(params['url'])
        r = client.request(url)
        result = client.parseDOM(r, 'div', attrs={'class':'item-thumbnail'})
        for item in result:
            h = HTMLParser()
            item = h.unescape(item)
            link = str(client.parseDOM(item, 'a', ret='href')[0])
            title = str(client.parseDOM(item, 'a', ret='title')[0])
            thumb = str(client.parseDOM(item, 'img', ret='src')[0])
            addLink(title, link, 12, thumb, thumb, '', 'Bajka', '')
    except:
        return

def WyciaganieLinku():
    try:
        url = urllib.unquote_plus(params['url'])
        r = client.request(url)
        video_url = client.parseDOM(r, 'iframe', ret='src')[0]
        return video_url
    except:
        return

def PlayVideo(url):
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))

############################################################################################################
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


###############################################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#

if mode == None:
    HOME()
elif mode == 1:
    debug=1
elif mode == 2:
    url = urllib.unquote_plus(params['url'])
    PlayVideo(url)
elif mode == 5:
    url = urllib.unquote_plus(params['url'])
    r = client.request(url)
elif mode == 10:
    ListowanieBajek()
elif mode == 11:
    ListowanieOdcinkow()
elif mode == 12:
    url = WyciaganieLinku()
    PlayVideo(url)

###################################################################################
xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)