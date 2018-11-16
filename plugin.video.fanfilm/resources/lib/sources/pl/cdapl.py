# -*- coding: utf-8 -*-
'''
    Covenant Add-on
    Copyright (C) 2018 :)

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

import urllib, urlparse, re, xbmcplugin, sys, xbmc, urllib2, requests, HTMLParser
from HTMLParser import HTMLParser

from ptw.libraries import source_utils, dom_parser,control
from ptw.libraries import cleantitle
from ptw.libraries import client, cache
from ptw.debug import log_exception, log


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['cda.pl']

        self.base_link = 'https://www.cda.pl/'
        self.search_link = 'video/show/%s?duration=dlugie&section=&quality=720p&section=&s=best&section='
        
    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False
 
    def contains_all_wors(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True
  
    def search(self, title, localtitle, year, is_movie_search):
        try:
            titles= []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))
            
            for title in titles:
                url = urlparse.urljoin(self.base_link, self.search_link)
                url = url % urllib.quote(str(title).replace(" ","_"))
                result = client.request(url)
                result = result.decode('utf-8')
                h = HTMLParser()
                result = h.unescape(result)
                result = client.parseDOM(result, 'div', attrs={'class': 'video-clip-wrapper'})

                for item in result:
                    link = str(client.parseDOM(item, 'a', ret='href')[0])
                    nazwa = str(client.parseDOM(item, 'a', attrs={'class': 'link-title-visit'})[0])
                    name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                    name = name.replace("  "," ")
                    title = title.replace("  "," ")
                    words = title.split(" ")
                    if self.contains_all_wors(name, words) and str(year) in name:
                        return link
        except Exception as e:
            log_exception()
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, True)

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            url = self.base_link + url
            result = client.request(url)
            title = client.parseDOM(result, 'span', attrs={'style': 'margin-right: 3px;'})[0]
            lang, info = self.get_lang_by_type(title)
            valid, host = source_utils.is_host_valid(url, hostDict)
            if not valid: return sources
            if "?wersja=1080p" in result:
                sources.append({'source': host, 'quality': '1080p', 'language': lang, 'url': url + "?wersja=1080p", 'info': info, 'direct': False, 'debridonly': False})
            if "?wersja=720p" in result:
                sources.append({'source': host, 'quality': 'HD', 'language': lang, 'url': url + "?wersja=720p", 'info': info, 'direct': False, 'debridonly': False})
            if "?wersja=480p" in result:
                sources.append({'source': host, 'quality': 'SD', 'language': lang, 'url': url + "?wersja=480p", 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except:
            log_exception()
            return sources

    def get_lang_by_type(self, lang_type):
        if "dubbing" in lang_type.lower():
            if "kino" in lang_type.lower():
                return 'pl', 'Dubbing Kino'
            return 'pl', 'Dubbing'
        elif 'napisy pl' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'napisy' in lang_type.lower():
            return 'pl', 'Napisy'
        elif 'lektor pl' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'lektor' in lang_type.lower():
            return 'pl', 'Lektor'
        elif 'POLSKI' in lang_type.lower():
            return 'pl', None
        elif 'pl' in lang_type.lower():
            return 'pl', None
        return 'en', None

    def resolve(self, url):
        link = str(url).replace("//","/").replace(":/", "://").split("?")[0]
        return str(link)

