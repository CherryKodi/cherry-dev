# -*- coding: utf-8 -*-

'''
    Covenant Add-on
    Copyright (C) 2017 homik

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib, urlparse, re, xbmcplugin, sys, xbmc, urllib2, socket, random

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client

proxyList = ['90.187.51.41:8080', '195.4.154.160:3128','149.202.0.60:3128','83.18.150.53:3128','83.18.150.52:3128','188.214.135.162:8088','89.37.0.68:8080']
random.shuffle(proxyList)

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['fili.cc']

        self.base_link = 'https://fili.cc'
        self.url_transl = 'embed?type=%s&code=%s&code2=%s&salt=%s'
        self.search_link = 'szukaj?q=%s'
        self.episode_link = '-Season-%01d-Episode-%01d'
        self.proxy = False
        self.proxy_ip = ''
        #self.setProxy()

    def setProxy(self):
        if xbmcplugin.getSetting(int(sys.argv[1]), 'proxy') == "true":
                for item in proxyList:
                    if self.is_bad_proxy(item):
                        print "Bad Proxy", item
                    else:
                        print "Good Proxy", item
                        self.proxy_ip = str(item)
                        self.proxy = True
                        break

    def is_bad_proxy(self,pip):
        try:        
            proxy_handler = urllib2.ProxyHandler({'http': pip})        
            opener = urllib2.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib2.install_opener(opener)        
            req=urllib2.Request('http://alltube.pl')  # change the url address here
            sock=urllib2.urlopen(req)
        except urllib2.HTTPError, e:        
            print 'Error code: ', e.code
            return e.code
        except Exception, detail:

            print "ERROR:", detail
            return 1
        return 0

    def check_titles(self, cleaned_titles, found_titles):   
        test = cleaned_titles[0] == cleantitle.get(found_titles[0]) or cleaned_titles[1] == cleantitle.get(found_titles[1]) or cleaned_titles[0] == cleantitle.get(found_titles[1]) or cleaned_titles[1] == cleantitle.get(found_titles[0])     
        return test  
    
    def do_search(self, title, localtitle, year, is_movie_search):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % urllib.quote(title)
            result = self.getUrlRequestData(url,self.proxy)
            result = result.decode('utf-8')

            result = client.parseDOM(result, 'ul', attrs={'id': 'resultList2'})
            li_list = []
            for el in result:
                li_list.extend(client.parseDOM(el, 'li'))
            

            result = [(client.parseDOM(i, 'a', ret='href')[0],
                       client.parseDOM(i, 'div', attrs={'class': 'title'})[0],
                       (client.parseDOM(i, 'div', attrs={'class': 'title_org'}) + [None])[0],
                       client.parseDOM(i, 'div', attrs={'class': 'info'})[0],
                       ) for i in li_list]

            search_type = 'Film' if is_movie_search else 'Serial'
            cleaned_titles = [cleantitle.get(title), cleantitle.get(localtitle)]
            # filter by name
            result = [x for x in result if self.check_titles(cleaned_titles, [x[2], x[1]])]
            # filter by type
            result = [x for x in result if x[3].startswith(search_type)]
            # filter by year
            result = [x for x in result if x[3].endswith(str(year))]

            if len(result) > 0:
                return result[0][0]
            else:
                return

        except :
            return

    def getUrlRequestData(self,url,proxy = False):
        import requests
        proxyDict = {
            "http" : self.proxy_ip,
        }
        if proxy:
            r = requests.get(url,proxies = proxyDict)
            return r.content
        else:
            r = requests.get(url)
            return r.content

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.do_search(title, localtitle, year, True)

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.do_search(tvshowtitle, localtvshowtitle, year, False)

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.urljoin(self.base_link, url)
            result = self.getUrlRequestData(url,self.proxy)
            result = client.parseDOM(result, 'ul', attrs={'data-season-num': season})[0]
            result = client.parseDOM(result, 'li')
            for i in result:
                s = client.parseDOM(i, 'a', attrs={'class': 'episodeNum'})[0]
                e = int(s[7:-1])
                if e == int(episode):
                    return client.parseDOM(i, 'a', attrs={'class': 'episodeNum'}, ret='href')[0]

        except :
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            typ = ''
            
            if url == None: return sources
            if "serial" in url:
                typ = "episode"
            if "film" in url:
                typ = "movie"
            url = urlparse.urljoin(self.base_link, url)
            result = self.getUrlRequestData(url,self.proxy)
            html = result
            result = client.parseDOM(result, 'div', attrs={'id': 'links'})
            attr = client.parseDOM(result, 'ul', ret='data-type')
            result = client.parseDOM(result, 'ul')
            for x in range(0, len(attr)):
                transl_type = attr[x]
                links = result[x+1]
                sources += self.extract_sources(transl_type, links, typ, html)

            return sources
        except:
            return sources

    def get_lang_by_type(self, lang_type):
        if lang_type == 'DUBBING':
            return 'pl', 'Dubbing'
        elif lang_type == 'NAPISY_PL':
            return 'pl', 'Napisy'
        if lang_type == 'LEKTOR_PL':
            return 'pl', 'Lektor'
        if lang_type == 'LEKTOR_AMATOR':
            return 'pl', 'Lektor'
        elif lang_type == 'POLSKI':
            return 'pl', None
        return 'en', None

    def extract_sources(self, transl_type, links, typ, html):
        sources = []
        if typ == "episode":
            test = re.search("""data-code="(.*)" data-code2="(.*)"><div class="container"><section""",html)
            code = test.group(1)
            code2 = test.group(2)
        if typ == "movie":
            test = re.search("""data-code="(.*)"><div class="container"><section""",html)
            code = test.group(1)
            code2 = "undefinded"
        data_refs = client.parseDOM(links, 'li', ret='data-ref')
        result = client.parseDOM(links, 'li')

        lang, info = self.get_lang_by_type(transl_type)

        for i in range(0, len(result)):

            el = result[i];
            host = client.parseDOM(el, 'span', attrs={'class': 'host'})[0]
            quality = client.parseDOM(el, 'span', attrs={'class': 'quality'})[0]
            q = 'SD'
            if quality.endswith('720p'):
                q = 'HD'
            elif quality.endswith('1080p'):
                q = '1080p'

            sources.append({'source': host, 'quality': q, 'language': lang, 'url': (typ,code,code2,data_refs[i]), 'info': info, 'direct': False, 'debridonly': False})

        return sources

    def resolve(self, url):
        try:
            url_to_exec = urlparse.urljoin(self.base_link, self.url_transl) % (url[0],url[1],url[2],url[3])
            result = self.getUrlRequestData(url_to_exec,self.proxy)

            search_string = "var url = '";
            begin = result.index(search_string) + len(search_string)
            end = result.index("'", begin)

            result_url = result[begin:end]
            result_url = result_url.replace('#WIDTH', '100')
            result_url = result_url.replace('#HEIGHT', '100')
            if 'streamango' in result_url:
                result_url = urlparse.urljoin(result_url,'?db=1&fbid=acllnmfkekmlodko')
                result_url = result_url.replace('https','http')
            return result_url
        except:
            return
