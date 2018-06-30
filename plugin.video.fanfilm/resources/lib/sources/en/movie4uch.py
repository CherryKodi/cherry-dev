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

import re, urlparse, urllib, json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import cache
from resources.lib.libraries import dom_parser2
from resources.lib.libraries import source_utils
import requests

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movie4u.ch','movie4u.live']
        self.base_link = 'https://movie4u.live'
        self.search_link = '/?s=%s'
        self.tv_search_link = '/wp-json/dooplay/search/?keyword=%s&nonce=b25f8f344b'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
            r = client.request(search_url)
            r = client.parseDOM(r, 'div', {'class': 'result-item'})
            r = [(dom_parser2.parse_dom(i, 'a', req='href')[0],
                  re.sub('<.*?>', '' , re.findall('alt=\"(.*?)\"', i)[0]),
                  dom_parser2.parse_dom(i, 'span', attrs={'class': 'year'})) for i in r]

            r = [(i[0].attrs['href'], i[1], i[2][0].content) for i in r if
                 (cleantitle.get(i[1]) == cleantitle.get(title) and i[2][0].content == year)]
            url = r[0][0]
    
            return url
        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(tvshowtitle)
            search_url = urlparse.urljoin(self.base_link, self.tv_search_link % clean_title.replace('-', '+'))
            r = client.request(search_url)
            r = json.loads(r)
            url = [(r[i]['url']) for i in r if
                 (cleantitle.get(r[i]['title']) == cleantitle.get(tvshowtitle))]
            url = source_utils.strip_domain(url[0])

            return url
        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            t = url.split('/')[2]
            url = self.base_link + '/episodes/%s-%dx%d' % (t, int(season), int(episode))
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = client.request(url)
            try:
                data = client.parseDOM(r, 'div', attrs={'class': 'playex'})
                data = [client.parseDOM(i, 'a', ret='href') for i in data if i]
                r = client.request(data[0][0])
                data = client.parseDOM(r, 'div', attrs={'class': 'playex'})
                data = [client.parseDOM(i, 'iframe', ret='src') for i in data if i]
                try:
                    for url in data[0]:
                        valid, host = source_utils.is_host_valid(url,hostDict)
                        if host == self.domains[1]:
                            r = requests.head(url)
                            url = r.headers['location']
                            valid, host = source_utils.is_host_valid(url,hostDict)
                        quality, info = source_utils.get_release_quality(url, None)
                        if not valid: continue
                        host = host.encode('utf-8')
                        sources.append({
                            'source': host,
                            'quality': quality,
                            'language': 'en',
                            'url': url.replace('\/', '/'),
                            'direct': False,
                            'debridonly': False
                    })
                except Exception:
                    pass
            except Exception:
                pass

            return sources
        except Exception:
            return

    def resolve(self, url):

        return url