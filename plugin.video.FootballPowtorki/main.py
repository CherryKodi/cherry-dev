# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests,json
from resources.lib.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys

reload(sys)
sys.setdefaultencoding('utf8')

pluginName=sys.argv[0].replace('plugin://','')
basePath = "special://home/addons/"+pluginName+"resources/media/"
resourcesPath = xbmc.translatePath(basePath)
default_background = resourcesPath + "default.jpg"
#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#
def CATEGORIES():
    #addDir("Szukaj", '', 1, '','','', True)
    addDir("Premier Ligue", "http://www.replaymatches.com/search/label/search/label/Premier%20League", 2, resourcesPath + "pl.png",default_background,'', True)
    addDir("La Liga", "http://www.replaymatches.com/search/label/La%20Liga", 2, resourcesPath + "laliga.png",default_background,'', True)
    addDir("Serie A", "http://www.replaymatches.com/search/label/Serie%20A", 2, resourcesPath + "seriea.png",default_background,'', True)
    addDir("Bundesliga", "http://www.replaymatches.com/search/label/Bundesliga", 2, resourcesPath + "bundesliga.png",default_background,'', True)
    addDir("Ligue1", "http://www.replaymatches.com/search/label/Ligue%201", 2, resourcesPath + "ligue1.png",default_background,'', True)
    addDir("Champions League", "http://www.replaymatches.com/search/label/UCL", 2, resourcesPath + "uefa.png",default_background,'', True)
    addDir("Europa League", "http://www.replaymatches.com/search/label/UEL", 2, resourcesPath + "europa.png",default_background,'', True)
    #addDir("FIFA", '', 9, '','','', True) TODO

def SUBCATEGORIES(mode):
    debug=1
###################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#

    
def addDir(name, url, mode, iconimage, thumb, opis, isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconimage, thumbnailImage=thumb)
    url = thumb
    liz.setArt({'thumb': iconimage,
                'icon': iconimage,
                'fanart': url})
    liz.setInfo("Video", {'title':name , 'genre':'', 'rating': 0, 'plot': opis})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def ListowanieMeczy():
    #import pydevd
    #pydevd.settrace(stdoutToServer=True, stderrToServer=True)
    url = urllib.unquote_plus(params['url'])
    result = client.request(url)
    result_images = client.parseDOM(result, 'article', attrs={'class':'post hentry'})
    result = client.parseDOM(result, 'h2', attrs={'class':'post-title entry-title'})
    
    images = client.parseDOM(result_images, 'a', ret='content')
    links = client.parseDOM(result, 'a', ret='href')
    titles = client.parseDOM(result, 'a', ret='title')
    for item in zip(links,titles,images):
        link = str(item[0])
        title = str(item[1])
        image = str(item[2])
        addDir(title, link, 3, image,default_background,'', True)
        
def ListowanieLinkow():
    url = urllib.unquote_plus(params['url'])
    result = client.request(url)
    nazwy = client.parseDOM(result, 'a', attrs={'class':'link-iframe'})
    result = client.parseDOM(result, 'div', attrs={'dir':'ltr'})[2]
    linki = client.parseDOM(result, 'a', ret='href')[1:len(nazwy)+1]
    for item in zip(linki,nazwy):
        link = str(item[0])
        title = str(item[1])
        addDir(title, link, 6, '',default_background,'', False)

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
    ListowanieMeczy()
elif mode == 3 :
    ListowanieLinkow()
elif mode == 6 : 
    url = urllib.unquote_plus(params['url'])
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
    
###################################################################################
xbmcplugin.endOfDirectory(int(sys.argv[1]))