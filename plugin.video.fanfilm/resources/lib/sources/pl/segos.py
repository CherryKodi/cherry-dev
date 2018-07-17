# -*- coding: utf-8 -*-

'''
    Covenant Add-on
    Copyright (C) 2018 CherryTeam

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

#import pydevd
#pydevd.settrace(stdoutToServer=True, stderrToServer=True)
from ptw.libraries import source_utils, dom_parser, client, cleantitle,control
from resources.lib.libraries import more_sources
import urllib, urlparse
import requests,re


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['segos.es']
        self.user_name = control.setting('segos.username')
        self.user_pass = control.setting('segos.password') 
        self.base_link = 'https://segos.es'
        self.search_link = '/?search=%s'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title,localtitle, year)

    def search(self, title, localtitle, year):
        try:
            simply_name = cleantitle.get(localtitle)
            simply_name2 = cleantitle.get(title)
            query = self.search_link % urllib.quote_plus(cleantitle.query(localtitle))
            url = urlparse.urljoin(self.base_link, query)
            headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Referer': 'https://segos.es/?page=login' }
            data ={"login" : self.user_name, 'password': self.user_pass,'loguj': ''}
            url = 'https://segos.es/?page=login'
            s = requests.Session()
            s.post('https://segos.es/?page=login',data=data,headers=headers)
            url=urlparse.urljoin(self.base_link,query)
            k = s.get(url)
            result = k.text
            
            results = client.parseDOM(result, 'div', attrs={'class':'col-lg-12 col-md-12 col-xs-12'})
            for result in results:
                segosurl = client.parseDOM(result, 'a', ret='href')[0]
                result = client.parseDOM(result, 'a')
                segostitles = cleantitle.get(result[1]).split('/')
                rok = str(result[1][-5:-1])
                for segostitle in segostitles:
                    if (simply_name == segostitle or simply_name2 == segostitle) and year == rok:
                        return urlparse.urljoin(self.base_link,segosurl)
                    continue
        except Exception, e:
            print str(e)
            return

    def search_ep(self, titles,season,episode):
        try:
            for title in titles:
                simply_name = cleantitle.get(title)
                query = self.search_link % str(title).replace(" ", "+")
                url = urlparse.urljoin(self.base_link, query)
                headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Referer': 'https://segos.es/?page=login' }
                data ={"login" : self.user_name, 'password': self.user_pass,'loguj': ''}
                url = 'https://segos.es/?page=login'
                s = requests.Session()
                s.post('https://segos.es/?page=login',data=data,headers=headers)
                url=urlparse.urljoin(self.base_link,query)
                k = s.get(url)
                result = k.text
                results = client.parseDOM(result, 'div', attrs={'class':'col-lg-12 col-md-12 col-xs-12'})
                for result in results:
                    segosurl = client.parseDOM(result, 'a', ret='href')[0]
                    segosurl = segosurl + "&s=%s&o=%s" % (season,episode)
                    result = client.parseDOM(result, 'a')
                    segostitles = cleantitle.get(result[1]).split('/')
                    for segostitle in segostitles:
                        if simply_name == segostitle:
                            link = urlparse.urljoin(self.base_link,segosurl)
                            return link
                        continue
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return {tvshowtitle,localtvshowtitle}

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search_ep(url ,season ,episode)    
    
    def sources(self, url, hostDict, hostprDict):

        sources = []
        try:
            if url == None: return sources
            headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Referer': 'https://segos.es/?page=login' }
            data ={"login" : self.user_name, 'password': self.user_pass,'loguj': ''}
            s = requests.Session()
            s.post('https://segos.es/?page=login',data=data,headers=headers)
            k = s.get(url)
            result = k.text
            result = client.parseDOM(result, 'table', attrs={'class':'table table-hover table-bordered'})                        
            results = client.parseDOM(result, 'tr')
            for result in results:
                try:
                    quality = client.parseDOM(result, 'td')[1]
                    quality = quality.replace(' [EXTENDED]','').replace(' [Extended]','')
                    lang = 'en'
                    info = client.parseDOM(result, 'td')[0]
                    info = client.parseDOM(info, 'img', ret='src')
                    if 'napisy' in info[0]: 
                        info[0] = 'Napisy'
                        lang = 'pl'
                    if 'lektor' in info[0]: 
                        info[0] = 'Lektor'
                        lang = 'pl'
                    if 'dubbing' in info[0]: 
                        info[0] = 'Dubbing'
                        lang = 'pl'
                    link = client.parseDOM(result, 'td')[5]
                    link = client.parseDOM(link, 'a', ret='href')
                    link = urlparse.urljoin(self.base_link,str(link[0]))
                    k = s.get(link)
                    video_link_content = k.text
                    video_link_content = client.parseDOM(video_link_content, 'div', attrs={'class':'embed-responsive embed-responsive-16by9'})
                    video_link = client.parseDOM(video_link_content, 'iframe', ret='src')
                    valid, host = source_utils.is_host_valid(video_link[0], hostDict)
                    more = False
                    for source in more_sources.more_cdapl(video_link[0],hostDict,lang,info[0]):
                        sources.append(source)
                        more = True
                    for source in more_sources.more_rapidvideo(video_link[0],hostDict,lang,info[0]):
                        sources.append(source)
                        more = True
                    if not more:
                        sources.append({'source': host, 'quality': quality, 'language': lang, 'url': video_link[0], 'info': info[0], 'direct': False, 'debridonly': False})
                except:
                    continue
            return sources
        except:
            return sources
    
    def resolve(self, url):
        return url
