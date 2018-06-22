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


import re,urllib,urlparse

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['project-free-tv.ch','project-free-tv.ag']
        self.base_link = 'http://www1.project-free-tv.ag'
        self.search_tv = '%s-season-%d-episode-%d/'
        self.search_link = '%s-%d/'
        self.search_link_2 = '/episode/%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            url = urlparse.urljoin(self.base_link, self.search_link_2 % (self.search_link % (clean_title, int(year))))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            clean_title = cleantitle.geturl(data['tvshowtitle'])
            url = urlparse.urljoin(self.base_link, self.search_link_2 % (self.search_tv % (clean_title, int(season), int(episode))))
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            r = client.request(url)
            links = re.findall('callvalue\((.+?)\)', r)
            try:
                quality = client.parseDOM(r, 'td', attrs={'id': 'quality'})[0]
            except:
                quality = 'SD'

            for i in links:
                try:
                    url = re.findall('(http.+?)(?:\'|\")', i)[0]
                    valid, host = source_utils.is_host_valid(url,hostDict)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


