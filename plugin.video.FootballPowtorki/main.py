# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests, json, resolveurl , sys

from ptw.libraries import addon_utils as addon
from ptw.libraries import source_utils, dom_parser, client, cleantitle

from ptw.debug import log_exception, log, start_trace, stop_trace, TRACE_ALL

_pluginName = sys.argv[0].replace('plugin://','')
_basePath = "special://home/addons/" + _pluginName + "resources/media/"
_resourcesPath = xbmc.translatePath(_basePath)
_default_background = _resourcesPath + "default.jpg"

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#

def CATEGORIES():
    addon.addDir("Premier Ligue", "http://www.replaymatches.com/search/label/search/label/Premier%20League", mode='ListowanieMeczy', icon=_resourcesPath + "pl.png", fanart=_default_background)
    addon.addDir("La Liga", "http://www.replaymatches.com/search/label/La%20Liga", mode='ListowanieMeczy', icon=_resourcesPath + "laliga.png", fanart=_default_background)
    addon.addDir("Serie A", "http://www.replaymatches.com/search/label/Serie%20A", mode='ListowanieMeczy', icon=_resourcesPath + "seriea.png", fanart=_default_background)
    addon.addDir("Bundesliga", "http://www.replaymatches.com/search/label/Bundesliga", mode='ListowanieMeczy', icon=_resourcesPath + "bundesliga.png", fanart=_default_background)
    addon.addDir("Ligue1", "http://www.replaymatches.com/search/label/Ligue%201", mode='ListowanieMeczy', icon=_resourcesPath + "ligue1.png", fanart=_default_background)
    addon.addDir("Champions League", "http://www.replaymatches.com/search/label/UCL", mode='ListowanieMeczy', icon=_resourcesPath + "uefa.png", fanart=_default_background)
    addon.addDir("Europa League", "http://www.replaymatches.com/search/label/UEL", mode='ListowanieMeczy', icon=_resourcesPath + "europa.png", fanart=_default_background)

############################################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#

def ListowanieMeczy():
    try:
        url = params['url']
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
            addon.addDir(title, link, mode='ListowanieLinkow', icon=image, fanart=_default_background)
    except:
        log_exception()

def ListowanieLinkow():
    try:
        url = params['url']
        result = client.request(url)
        nazwy = client.parseDOM(result, 'a', attrs={'class':'link-iframe'})
        result = client.parseDOM(result, 'div', attrs={'dir':'ltr'})[2]
        linki = client.parseDOM(result, 'a', ret='href')[1:len(nazwy)+1]
        for item in zip(linki,nazwy):
            link = str(item[0])
            title = str(item[1])
            addon.addLink(title, link, mode='OdpalanieLinku', fanart=_default_background)
    except:
        log_exception()

def OdpalanieLinku():
    url = params['url']
    addon.PlayMedia(url)

############################################################################################################
#=########################################################################################################=#
#                                               GET PARAMS                                                 #
#=########################################################################################################=#

params = addon.get_params()
url = params.get('url')
name = params.get('name')
mode = params.get('mode')
iconimage = params.get('iconimage')

############################################################################################################
#=########################################################################################################=#
#                                                   MODES                                                  #
#=########################################################################################################=#

if mode == None :
    CATEGORIES()
elif mode == 'ListowanieMeczy' :
    ListowanieMeczy()
elif mode == 'ListowanieLinkow' :
    ListowanieLinkow()
elif mode == 'OdpalanieLinku' : 
    OdpalanieLinku()

############################################################################################################

xbmcplugin.setContent(int(sys.argv[1]),'Movies')
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)