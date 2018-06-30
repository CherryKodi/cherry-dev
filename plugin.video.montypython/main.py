# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests
from ptw.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys

reload(sys)
sys.setdefaultencoding('utf8')

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#

def CATEGORIES():
    r = client.request('http://monty-python.org/')
    result = client.parseDOM(r, 'section', attrs={'id':'all'})
    kategorie = client.parseDOM(result, 'div', ret='onclick')
    nazwy = client.parseDOM(result, 'h4')
    opisy = client.parseDOM(result, 'p')
    obrazy = client.parseDOM(result, 'div', ret='style')
    counter = 0;
    for kategoria in kategorie:
        kategoria = str(kategoria).replace("location.href='", 'http://monty-python.org').replace("';", '')
        kategorie[counter] = kategoria
        obrazy[counter] = str(obrazy[counter]).replace("background-image: url('", 'http://monty-python.org').replace("')", '')
        opisy[counter] = str(opisy[counter]).replace("<br />","")
        addDir(str(nazwy[counter]), kategoria, 3, obrazy[counter],obrazy[counter],str(opisy[counter]), True)
        counter+=1

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
    
def addDir(name, url, mode, iconimage, thumb, opis, isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconimage, thumbnailImage=thumb)
    url = thumb
    liz.setArt({'thumb': thumb,
                'icon': iconimage,
                'fanart': url})
    liz.setInfo("Video", {'title':name , 'genre':'menu', 'rating': 0, 'plot': opis})
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


        
###################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#
if mode == None or url == None or len(url) < 1 :
    CATEGORIES()
elif mode == 1 :
    mySearch()
elif mode == 2 :
    myOther()
elif mode == 3 :
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    url = urllib.unquote_plus(params['url'])
    r = client.request(url)
    result = client.parseDOM(r, 'div', attrs={'class':'episodes'})
    linki = client.parseDOM(result, 'a', ret='href')
    nazwy = client.parseDOM(result, 'a')
    counter = 0
    for link in linki:
        linki[counter] = 'http://monty-python.org' + str(link)
        addDir(str(nazwy[counter]), linki[counter], 4, 'ikona.png','thumb.png',None, False)
        counter+=1    
elif mode == 4 : 
    url = urllib.unquote_plus(params['url'])
    r = client.request(url)
    link = client.parseDOM(r, 'iframe', ret='src')
    url = resolveurl.resolve(link[0])
    xbmc.Player().play(str(url))

###################################################################################
xbmcplugin.endOfDirectory(int(sys.argv[1]))