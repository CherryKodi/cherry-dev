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
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                    'Referer': 'http://iitvx.pl/'
                }
                data = {
                    'text': title,
                    }
                r = requests.post(self.search_link, data = data,headers=headers)
                result = r.text
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
                        link = client.parseDOM(result, 'a', ret='href')[0]
                        return link
        except Exception, e:
            print str(e)
            return

    def getlink(self,link):
        try:
            url = link
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                'Referer': url
            }
            r = requests.post(url, headers = headers)
            test = r.text.find('data-salt=')
            test2 = r.text.find('data-time')
            salt_value = r.text[test+11:test2-7]
            cookie = r.cookies._cookies['.iiv.pl']['/']['__cfduid'].name +'='+ r.cookies._cookies['.iiv.pl']['/']['__cfduid'].value
            cookie = cookie + '; ban=' + r.cookies._cookies['iiv.pl']['/']['ban'].value
            cookie = cookie + '; october_session=' + r.cookies._cookies['iiv.pl']['/']['october_session'].value
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                'Referer': url,
                'Cookie': cookie,
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host':    'iiv.pl',
                'X-OCTOBER-REQUEST-HANDLER': 'onAfterShortcutView',
                'X-OCTOBER-REQUEST-PARTIALS': 'shortcut/link_show',
                'X-Requested-With': 'XMLHttpRequest'
            }
            data = {
                'salt': salt_value,
                'blocker': '0'
            }
            r = requests.post(url, data = data,headers=headers)
            result = r.text
            result = result.replace("\/",'/')
            test = result.find('href=')+7
            test2 = result.find('\\" class=')
            result = result[test:test2]
            return result
        except Exception,e:
            print str(e)
            return

    def work(self, link):
        if str(link).startswith("http://"):
            link = self.getlink(link)
            q = source_utils.check_sd_url(link)
            valid, host = source_utils.is_host_valid(link, testDict)
            if not valid: return 0
            return host,q,link
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return {tvshowtitle,localtvshowtitle}

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search(url ,season ,episode)        

    def sources(self, url, hostDict, hostprDict):
        global testDict
        testDict = hostDict
        sources = []
        try:
            if url == None: return sources
            headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
                    'Referer': 'http://iitv.pl/'
            }
            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs={'class':'tab-wrapper'})[0]
            lektor = client.parseDOM(result, 'ul', attrs={'id':'lecPL'})
            if len(lektor) > 0:
                links = client.parseDOM(lektor, 'a', ret='href')
                from multiprocessing.dummy import Pool as ThreadPool
                pool = ThreadPool(10)
                results = pool.map(self.work,links)
                results = [x for x in results if x is not None]
                for result in results:
                    sources.append({'source': result[0], 'quality': result[1], 'language': 'pl', 'url': result[2], 'info': 'Lektor', 'direct': False, 'debridonly': False})
            napisy = client.parseDOM(result, 'ul', attrs={'id':'subPL'})
            if len(napisy) > 0:
                links = client.parseDOM(napisy, 'a', ret='href')
                from multiprocessing.dummy import Pool as ThreadPool
                pool = ThreadPool(10)
                results = pool.map(self.work,links)
                results = [x for x in results if x is not None]
                for result in results:
                    sources.append({'source': result[0], 'quality': result[1], 'language': 'pl', 'url': result[2], 'info': 'Napisy', 'direct': False, 'debridonly': False})
            eng = client.parseDOM(result, 'ul', attrs={'id':'org'})
            if len(eng) > 0:
                links = client.parseDOM(eng, 'a', ret='href')
                from multiprocessing.dummy import Pool as ThreadPool
                pool = ThreadPool(10)
                results = pool.map(self.work,links)
                results = [x for x in results if x is not None]
                for result in results:
                    sources.append({'source': result[0], 'quality': result[1], 'language': 'en', 'url': result[2], 'info': 'ENG', 'direct': False, 'debridonly': False})
            return sources
        except Exception, e:
            print str(e)
            return sources
    
    def resolve(self, url):
        return url      
