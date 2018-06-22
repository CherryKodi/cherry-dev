# -*- coding: utf-8 -*-

'''
    Incursion Add-on
    Copyright (C) 2016 Incursion

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


import re,urllib,urlparse,json,base64,hashlib,time

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import source_utils
from resources.lib.libraries import dom_parser




class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['tvbox.ag']
        self.base = 'https://tvbox.ag'
        self.basealt = 'https://tvbox.bypassed.eu'
        self.search_link = 'search?q=%s'

    def basetester(self):
        try:
            r = client.request(self.base)
            self.base_link = self.basealt if r == None else self.base
        except:
			self.base_link = self.basealt
        
    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            self.basetester()
            url = urlparse.urljoin(self.base_link, self.search_link %cleantitle.geturl(title).replace('-','+'))
            r = client.request(url, cookie='check=2')
            m = dom_parser.parse_dom(r, 'div', attrs={'class': 'masonry'})
            m = dom_parser.parse_dom(m, 'a', req='href')
            m = [(i.attrs['href']) for i in m if i.content == title]
            url = urlparse.urljoin(self.base_link,m[0])
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            self.basetester()
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)
            url = urlparse.urljoin(self.base_link, self.search_link %cleantitle.geturl(data['tvshowtitle']).replace('-','+'))
            r = client.request(url, cookie='check=2')
            m = dom_parser.parse_dom(r, 'div', attrs={'class': 'masonry'})
            m = dom_parser.parse_dom(m, 'a', req='href')
            m = [(i.attrs['href']) for i in m if i.content == data['tvshowtitle']]
            query = '%s/season-%s/episode-%s/'%(m[0],season,episode)
            url = urlparse.urljoin(self.base_link,query)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return
            r = client.request(url, cookie='check=2')

            m = dom_parser.parse_dom(r, 'table', attrs={'class': 'show_links'})[0]
            links = re.findall('k">(.*?)<.*?f="(.*?)"',m.content)
            for link in links:
                try:
                    sources.append({'source': link[0], 'quality': 'SD', 'language': 'en', 'url': link[1], 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        r = client.request(url)
        r = dom_parser.parse_dom(r, 'div', {'class': 'link_under_video'})
        r = dom_parser.parse_dom(r, 'a', req='href')
        return r[0].attrs['href']
