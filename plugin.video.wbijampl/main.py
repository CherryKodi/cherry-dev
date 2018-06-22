# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests,json
from resources.lib.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys

reload(sys)
sys.setdefaultencoding('utf8')

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#
def CATEGORIES():
    url = "http://www.accelworld.wbijam.pl/pierwsza_seria.html"
    result = requests.get(url).content
    result = client.parseDOM(result, 'ul', attrs={'class':'pmenu'})[4]
    result = client.parseDOM(result, 'li')
    for item in result:
        link = client.parseDOM(item, 'a', ret='href')[0]
        nazwa = client.parseDOM(item, 'a')[0]
        if "Pozosta" in str(nazwa) or "Anime" in str(nazwa):
            continue
        addDir(str(nazwa), str(link), 2, '','','', True)

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
    liz.setArt({'thumb': thumb,
                'icon': iconimage,
                'fanart': url})
    liz.setInfo("Video", {'title':name , 'genre':'', 'rating': 0, 'plot': opis})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def ListujSezony():
    #import pydevd
    #pydevd.settrace(stdoutToServer=True, stderrToServer=True)
    url = urllib.unquote_plus(params['url'])
    result = requests.get(url).content
    result = client.parseDOM(result, 'ul', attrs={'class':'pmenu'})[1]
    result = client.parseDOM(result, 'li')
    for item in result:
        link = client.parseDOM(item, 'a', ret='href')[0]
        nazwa = client.parseDOM(item, 'a')[0]
        if "Kolejno" in str(nazwa):
            continue
        addDir(str(nazwa), url + str(link), 3, '','','', True)

def ListujOdcinki():
    url = urllib.unquote_plus(params['url'])
    result = requests.get(url).content
    result = client.parseDOM(result, 'table', attrs={'class':'lista'})[0]
    result = client.parseDOM(result, 'tr', attrs={'class':'lista_hover'})
    for item in result:
        link = client.parseDOM(item, 'a', ret='href')[0]
        nazwa = str(client.parseDOM(item, 'img')[0]).split("</a>")
        nazwa = nazwa[0]
        data = client.parseDOM(item, 'td', attrs={'class':'center'})[1]
        url = url.split("pl/")[0] + "pl/"
        addDir(str(data) + " [B]" + str(nazwa) +"[/B]", url + str(link), 4, '','','', True)
        
def ListujLinki():
    url = urllib.unquote_plus(params['url'])
    result = requests.get(url).content
    result = client.parseDOM(result, 'table', attrs={'class':'lista'})
    result = client.parseDOM(result, 'tr', attrs={'class':'lista_hover'})
    odtwarzacz = "%sodtwarzacz-%s.html"
    hostDict = resolveurl.relevant_resolvers(order_matters=True)
    hostDict = [i.domains for i in hostDict if not '*' in i.domains]
    hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
    hostDict = [x for y,x in enumerate(hostDict) if x not in hostDict[:y]]
    url = url.split("pl/")[0] + "pl/"
    for item in result:
        id = client.parseDOM(item, 'span', ret='rel')[0]
        content = odtwarzacz % (url,id)
        xbmc.log('Wbijam.pl | Listuje z url: %s' % content, xbmc.LOGNOTICE)
        temp = requests.get(content).content
        try:
            link = client.parseDOM(temp, 'iframe', ret='src')
        except:
            continue
        for item2 in link:
            try:
                if str(item2).startswith("//"):
                    item2 = str(item2).replace("//","http://")
                valid, host = source_utils.is_host_valid(str(item2), hostDict)
                if valid == False:
                    continue
                xbmc.log('Wbijam.pl | Video Link: %s' % str(item2), xbmc.LOGNOTICE)
                addDir("[B]" + host + "[/B]", str(item2), 6, '','','', False)
            except:
                continue
        
    
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
    ListujSezony()
elif mode == 3 :
    ListujOdcinki()
elif mode == 4 :
    ListujLinki()
elif mode == 6 : 
    url = urllib.unquote_plus(params['url'])
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
    
###################################################################################
xbmcplugin.endOfDirectory(int(sys.argv[1]))