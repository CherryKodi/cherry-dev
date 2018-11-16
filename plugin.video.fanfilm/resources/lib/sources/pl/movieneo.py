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
import json

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['movieneo.com']
        
        self.base_link = 'https://movieneo.com'
        self.search_link = '/search-results/%s'
        self.streaminit = 'https://movieneo.com/cdn/stream/init/'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title,localtitle, year)

    
    def search(self, title, localtitle, year):
        try:
            import sys  
            reload(sys)  
            sys.setdefaultencoding('utf8')
            simply_name = cleantitle.get(localtitle)
            simply_name2 = cleantitle.get(title)
            simply_name = cleantitle.query(localtitle).split(' ')
            simply_name2 = cleantitle.query(title).split(' ')
            query = self.search_link % urllib.quote_plus(cleantitle.query(localtitle))
            url = urlparse.urljoin(self.base_link, query)
            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs={'class':'row search-results'})
            results = client.parseDOM(result, 'div', attrs={'class':'item-detail-bigblock title title-bigblock'})
            for result in results:
                movieneourl = client.parseDOM(result, 'a', ret='href')[0]
                result = client.parseDOM(result, 'a')[0]
                for word in simply_name:
                    if word in result and year in result:
                        return [urlparse.urljoin(self.base_link,movieneourl),result]
                    continue
        except Exception, e:
            print str(e)
            return    
        
    def sources(self, url, hostDict, hostprDict):
        
        sources = []
        try:
            if url == None: return sources
            result = client.request(url[0])
            id = client.parseDOM(result, 'meta',ret='content')
            for item in id:
                if '?f=' in item:
                    index = item.find('=')
                    id = item[index+1:]
                    break
            result = client.request(self.streaminit+str(id)).replace('\\u0022', '\"')
            quality = []
            info = ''
            url[1] = url[1].lower()
            if '1080p' in result:
                quality.append('1080p')
            if '720p' in result:
                quality.append('720p')
            if '480p' in result:
                quality.append('SD')
            if '360p' in result:
                quality.append('SD')
            if 'lektor' in url[1]:
                info = 'Lektor'
            if 'pl' in url[1]:
                info = 'Lektor'
            if 'napisy' in url[1]:
                info = 'Napisy'
            if 'dub' in url[1]:
                info = 'Dubbing'
            if 'dubbing' in url[1]:
                info = 'Dubbing'
            index_stream_start = result.find('"streamUrl":"')+13
            index_stream_end = result.find('","refreshUrl')
            result = result[index_stream_start:index_stream_end]
            result = result.replace('\\u0026','&').replace('\\','').replace('\\','').replace('\\','').replace('\\','').replace('\\','').replace('\\','').replace('n=','n='+quality[0]+'_')
            url[0] = 'https://'+result
            sources.append({'source': 'Movieneo', 'quality': quality[0], 'language': 'pl', 'url': url[0], 'info': info, 'direct': True, 'debridonly': False})
            return sources
        except:
            return sources
    
    def resolve(self, url):
        return url      
