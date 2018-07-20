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

from ptw.libraries import source_utils, dom_parser, client, cleantitle
import urllib, urlparse
import requests
from ptw.debug import log_exception, log

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['iitvx.pl']
        
        self.base_link = 'http://iitvx.pl/'
        self.search_link = 'http://iitvx.pl/szukaj'

    def search(self, titles,season,episode):
        try:
            for title in titles:
                log("FanFilm.IITVX Wyszukiwanie serialu po tytule: %s" % title)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                    'Referer': 'http://iitvx.pl/'
                }
                data = {'text': title}
                result = client.request(self.search_link, post=data, headers=headers)
                if result is None:
                    continue
                query = 'S00E00'
                if int(season)<10:
                    query = query.replace('S00', 'S0'+season)
                if int(season)>=10:
                    query = query.replace('S00', 'S'+season)
                if int(episode)<10:
                    query = query.replace('E00', 'E0'+episode)
                if int(episode)>=10:
                    query = query.replace('E00', 'E'+episode)
                result = client.parseDOM(result, 'div', attrs={'class':'episodes-list'})
                results = client.parseDOM(result, 'li')
                for result in results:
                    test = client.parseDOM(result, 'span')[1]
                    if query == str(test):
                        log("FanFilm.IITVX Znalazlem odcinek: %s" % query)
                        link = client.parseDOM(result, 'a', ret='href')[0]
                        log("FanFilm.IITVX Znalazlem serial pod linkiem: %s" % link)
                        return link
        except Exception:
            log_exception()
            return

    def work(self, link, testDict):
        if str(link).startswith("http"):
            q = source_utils.check_sd_url(link)
            valid, host = source_utils.is_host_valid(link, testDict)
            if not valid: return 0
            return host, q, link
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return {tvshowtitle,localtvshowtitle}

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search(url ,season ,episode)        

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None: return sources
            headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                    'Referer': 'http://iitv.pl/'
            }
            output = client.request(url)
            output = client.parseDOM(output, 'div', attrs={'class':'tab-wrapper'})[0]
            lektor = client.parseDOM(output, 'ul', attrs={'id':'lecPL'})
            if len(lektor) > 0:
                links = client.parseDOM(lektor, 'a', ret='href')
                for link in links:
                    try:
                        result = self.work(link, hostDict)
                        sources.append({'source': result[0], 'quality': result[1], 'language': 'pl', 'url': result[2], 'info': 'Lektor', 'direct': False, 'debridonly': False})
                    except:
                        continue
            napisy = client.parseDOM(output, 'ul', attrs={'id':'subPL'})
            if len(napisy) > 0:
                links = client.parseDOM(napisy, 'a', ret='href')
                for link in links:
                    try:
                        result = self.work(link, hostDict)
                        sources.append({'source': result[0], 'quality': result[1], 'language': 'pl', 'url': result[2], 'info': 'Napisy', 'direct': False, 'debridonly': False})
                    except:
                        continue
            eng = client.parseDOM(output, 'ul', attrs={'id':'org'})
            if len(eng) > 0:
                links = client.parseDOM(eng, 'a', ret='href')
                for link in links:
                    try:
                        result = self.work(link, hostDict)
                        sources.append({'source': result[0], 'quality': result[1], 'language': 'en', 'url': result[2], 'info': 'ENG', 'direct': False, 'debridonly': False})
                    except:
                        continue
            return sources
        except Exception:
            log_exception()
            return sources
    
    def resolve(self, url):
        return url      
