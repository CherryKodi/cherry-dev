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


import re,urllib,urlparse,json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import dom_parser
from resources.lib.libraries import source_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['onwatchseries.to','mywatchseries.to','dwatchseries.to']
        self.base_link = 'http://ewatchseries.io'
        self.search_link = 'https://ewatchseries.io/ajax-search.html'
        self.search_link_2 = 'http://ewatchseries.io/search/%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = cleantitle.geturl(title).replace('-','+')
            p = urllib.urlencode({'keyword': t,'id':1})
            r = client.request(self.search_link, post=p, XHR=True)
            try: r = json.loads(r)
            except: r = None
            r = dom_parser.parse_dom(r['content'], 'a', attrs={'class': 'ss-title'})
            url = '%s%s-e0.html' % (self.base_link, r[0].attrs['href'].replace('serie','episode'))
            return url
        except:
            return
            
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            q = cleantitle.geturl(url['tvshowtitle']).replace('-','+')
            t = q + '+season+%s' % season
            p = urllib.urlencode({'keyword': t,'id':1})
            r = client.request(self.search_link, post=p, XHR=True)
            try: r = json.loads(r)
            except: r = None
            r = dom_parser.parse_dom(r['content'], 'a', attrs={'class': 'ss-title'})
            url = '%s%s-e%s.html' % (self.base_link, r[0].attrs['href'].replace('serie','episode'), episode)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            r = client.request(url)
            data = client.parseDOM(r, 'div', attrs={'class': 'anime_muti_link'})
            data = [client.parseDOM(i, 'a', ret='data-video') for i in data if i]
            try:
                for link in data[0]:
                    url = 'http:' + link
                    valid, host = source_utils.is_host_valid(url,hostDict)
                    quality, info = source_utils.get_release_quality(url, None)
                    if not valid: continue
                    sources.append({
                        'source': host,
                        'quality': quality,
                        'language': 'en',
                        'url': url,
                        'direct': False,
                        'debridonly': False
                })
            except Exception:
                pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


