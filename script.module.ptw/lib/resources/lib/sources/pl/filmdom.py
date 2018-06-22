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
from resources.lib.libraries import source_utils, dom_parser, client, cleantitle,control
import urllib, urlparse,ast
import requests,re

class source:
    def __init__(self):
        
        self.priority = 1
        self.language = ['pl']
        self.domains = ['filmdom.pl']
        self.base_link = 'http://filmdom.pl'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title,localtitle, year)

    def contains_word(self, str_to_check, word):
        return re.search(r'\b' + word + r'\b', str_to_check, re.IGNORECASE)   
 
    def contains_all_wors(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True    

    def search(self, title, localtitle, year):
        try:
            searchtitles = (localtitle,title)
            for searchtitle in searchtitles:
                simply_name = cleantitle.normalize(cleantitle.getsearch(localtitle))
                simply_name2 = cleantitle.normalize(cleantitle.getsearch(title))
    
                data = {
                    's': str(cleantitle.getsearch(searchtitle)),
                    'search-form':'5'
                }
                
                response = requests.post(self.base_link, data = data)
                result = response.text
                
                result = client.parseDOM(result, 'ul', attrs={'class':'film-num-list'})
                titles = client.parseDOM(result, 'a')
                links = client.parseDOM(result, 'a', ret='href')
                rok = client.parseDOM(result, 'li')
                counter = 0
                for item in zip(titles,links):
                    if not str(item[1]).startswith("http://filmdom.pl/films/"):
                        continue
                    rok_film = str(rok[counter][-4:])
                    counter +=1
                    t2 = item[0].split(" / ")
                    for tytul in t2:
                        tytul = tytul.split(" (")
                        words = cleantitle.normalize(cleantitle.getsearch(tytul[0])).split(" ")
                        if (self.contains_all_wors(simply_name, words) or self.contains_all_wors(simply_name2, words)) and year == rok_film:
                            return item[1]
            return
        except Exception, e:
            print str(e)
            return

    def search_ep(self, titles,season,episode,year):
        try:
            searchtitles = titles
            for searchtitle in searchtitles:
                simply_name = cleantitle.normalize(cleantitle.getsearch(searchtitle))
    
                data = {
                    's':cleantitle.normalize(cleantitle.getsearch(searchtitle)),
                    'search-form':'5'
                }
                
                response = requests.post(self.base_link, data = data)
                result = response.text
                
                result = client.parseDOM(result, 'ul', attrs={'class':'film-num-list'})
                if len(result) == 2:
                    result = result[1]
                titles = client.parseDOM(result, 'a')
                links = client.parseDOM(result, 'a', ret='href')
                rok = client.parseDOM(result, 'li')
                counter = 0
                for item in zip(titles,links):
                    if not str(item[1]).startswith("http://filmdom.pl/serials/"):
                        continue
                    rok_film = str(rok[counter][-4:])
                    counter +=1
                    t2 = item[0].split(" / ")
                    for tytul in t2:
                        if searchtitle == "Gra o tron":
                            year = "2011"
                        tytul = tytul.split(" (")
                        words = cleantitle.normalize(cleantitle.getsearch(tytul[0])).split(" ")
                        if self.contains_all_wors(simply_name, words) and year == rok_film:
                            return item[1]+"?sezon=%s&odcinek=%s" % (season,episode)  
            return
        except Exception, e:
            print str(e)
            return
    
    def get_lang_by_type(self, lang_type):
        if lang_type == 'Dubbing PL':
            return 'pl', 'Dubbing'
        elif lang_type == 'Napisy PL':
            return 'pl', 'Napisy'
        elif lang_type == 'Lektor PL':
            return 'pl', 'Lektor'
        elif lang_type == 'LEKTOR_AMATOR':
            return 'pl', 'Lektor'
        elif lang_type == 'POLSKI':
            return 'pl', None
        return 'en', None
    
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        titles = (tvshowtitle,localtvshowtitle)
        return titles,year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        titles = url[0]
        year = url[1]
        return self.search_ep(titles ,season ,episode,year) #url = titles
    
    def sources(self, url, hostDict, hostprDict):

        sources = []
        try:
            if url == None: return sources
            
            response = requests.get(url)
            result = response.text
            html = result
            result = client.parseDOM(result, 'tbody', attrs={'id':'all-links'})[0]
            result = client.parseDOM(result, 'tr')
            regtest = re.search("""PublicLink = (.*);""", html)
            x = ast.literal_eval(regtest.group(1).replace("\\",""))
            x = [n.strip() for n in x]
            for item in zip(result,x):
                try:
                    items = client.parseDOM(item[0], 'td')
                    if len(items) == 4:
                        id = client.parseDOM(items[0], 'button', ret='value')[0]
                        quality = str(items[1])
                        if "720" not in quality and "1080" not in quality:
                            quality = "SD"
                        info = items[2]
                        host = items[3]
                        link = item[1]
                        lang, info = self.get_lang_by_type(info)
                        sources.append({'source': host, 'quality': quality, 'language': lang, 'url': link, 'info': info, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources
    
    def resolve(self, url):
        return url      
