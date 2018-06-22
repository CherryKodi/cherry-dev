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
import re
import urllib
import urlparse
import json
import ast
import xbmc
import httplib

from resources.lib.libraries import client, cleantitle, directstream, jsunpack, source_utils
from resources.lib.libraries import dom_parser


class source:
    def __init__(self):
        '''
        Constructor defines instances variables

        '''
        self.priority = 1
        self.language = ['en']
        self.domains = ['fmovies.se', 'fmovies.to', 'bmovies.to', 'bmovies.is']
        self.base_link = 'https://bmoviesfree.net'
        self.search_path = '/search-query/%s'
        self.film_path = '/film/%s'
        self.js_path = '/assets/min/public/all.js?5a0da8a9'
        self.info_path = '/ajax/episode/info?ts=%s&_=%s&id=%s&server=%s&update=0'
        self.grabber_path = '/grabber-api/?ts=%s&id=%s&token=%s&mobile=0'

    def movie(self, imdb, title, localtitle, aliases, year):
        '''
        Takes movie information and returns a set name value pairs, encoded as
        url params. These params include ts
        (a unqiue identifier, used to grab sources) and list of source ids

        Keyword arguments:

        imdb -- string - imdb movie id
        title -- string - name of the movie
        localtitle -- string - regional title of the movie
        year -- string - year the movie was released

        Returns:

        url -- string - url encoded params

        '''
        try:
            clean_title = cleantitle.geturl(title).replace('-','+')
            query = (self.search_path % clean_title)
            url = urlparse.urljoin(self.base_link, query)

            search_response = client.request(url)

            r = client.parseDOM(
                search_response, 'div', attrs={'class': 'row movie-list'})[0]

            r = dom_parser.parse_dom(r, 'a', req='href')
            url = [(i.attrs['href']) for i in r if cleantitle.get(title) in cleantitle.get(i.content)][0]

            r = client.request(url)
            quality = client.parseDOM(r, 'span', attrs={'class': 'quality'})[0]
            r = client.parseDOM(r, 'div', attrs={'class': 'mt row'})[0]
            sources_list = []
            try:
                if client.parseDOM(r, 'div', ret='data-streamgo')[0]:
                    sources_list.append('https://streamgo.me/player/%s' % client.parseDOM(r, 'div', ret='data-streamgo')[0])
            except Exception:
                pass
            try:
                if client.parseDOM(r, 'div', ret='data-server_openload')[0]:
                    sources_list.append('https://openload.co/embed/%s' % client.parseDOM(r, 'div', ret='data-server_openload')[0])
            except Exception:
                pass
            data = {
                'imdb': imdb,
                'title': title,
                'localtitle': localtitle,
                'year': year,
                'quality': quality,
                'sources': sources_list
            }
            url = urllib.urlencode(data)

            return url

        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        '''
        Takes TV show information, encodes it as name value pairs, and returns
        a string of url params

        Keyword arguments:

        imdb -- string - imdb tv show id
        tvdb -- string - tvdb tv show id
        tvshowtitle -- string - name of the tv show
        localtvshowtitle -- string - regional title of the tv show
        year -- string - year the tv show was released

        Returns:

        url -- string - url encoded params

        '''
        try:
            data = {
                'imdb': imdb,
                'tvdb': tvdb,
                'tvshowtitle': tvshowtitle,
                'year': year
            }
            url = urllib.urlencode(data)

            return url

        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        '''
        Takes episode information, finds the ts and list sources, encodes it as
        name value pairs, and returns a string of url params

        Keyword arguments:

        url -- string - url params
        imdb -- string - imdb tv show id
        tvdb -- string - tvdb tv show id
        title -- string - episode title
        premiered -- string - date the episode aired (format: year-month-day)
        season -- string - the episodes season
        episode -- string - the episode number

        Returns:

        url -- string - url encoded params

        '''
        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)

            clean_title = cleantitle.geturl(data['tvshowtitle']).replace('-','+')
            query = (self.search_path % clean_title)
            url = urlparse.urljoin(self.base_link, query)

            search_response = client.request(url)

            r = client.parseDOM(
                search_response, 'div', attrs={'class': 'row movie-list'})[0]

            r = dom_parser.parse_dom(r, 'a', req='href')
            url = [(i.attrs['href']) for i in r if '%s - Season %01d' % (data['tvshowtitle'], int(season)) in i.content][0]

            r = client.request(url)
            r = client.parseDOM(r, 'div', attrs={'id': 'player'})[0]

            url = client.parseDOM(r, 'a', ret='href')[0]
            film_response = client.request(url)

            servers = client.parseDOM(
                film_response, 'div', attrs={'id': 'servers'})[0]
            r = dom_parser.parse_dom(servers, 'a', req='title')
                
            url = [(i) for i in r if 'Episode %02d' % (int(episode)) in i.attrs['title']]
            sources_list = []

            for i in url:
                try:
                    if i.attrs['data-streamgo']:
                        sources_list.append('https://streamgo.me/player/%s' % i.attrs['data-streamgo'])
                except Exception:
                    pass
                try:
                    if i.attrs['data-openload']:
                        sources_list.append('https://openload.co/embed/%s' % i.attrs['data-openload'])
                except Exception:
                    pass
            quality = client.parseDOM(film_response, 'span', attrs={'class': 'quality'})[0]

            data.update({
                'title': title,
                'premiered': premiered,
                'season': season,
                'episode': episode,
                'quality': quality,
                'sources': sources_list
            })

            url = urllib.urlencode(data)

            return url

        except:
            return

    def sources(self, url, hostDict, hostprDict):
        '''
        Loops over site sources and returns a dictionary with corresponding
        file locker sources and information

        Keyword arguments:

        url -- string - url params

        Returns:

        sources -- string - a dictionary of source information

        '''

        sources = []

        try:
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)

            data['sources'] = ast.literal_eval(data['sources'])

            for i in data['sources']:
                try:
                    valid, host = source_utils.is_host_valid(i,hostDict)
                    quality = 'HD' if '720p' in data['quality'] else data['quality']

                    sources.append({
                        'source': host,
                        'quality': quality,
                        'language': 'en',
                        'url': i,
                        'direct': False,
                        'debridonly': False
                    })
                except Exception:
                    pass

            return sources

        except:
            return sources

    def resolve(self, url):
        '''
        Takes a scraped url and returns a properly formatted url

        Keyword arguments:

        url -- string - source scraped url

        Returns:

        url -- string - a properly formatted url

        '''
        try:
            return url

        except Exception:
            return

    def __token(self, dic):
        '''
        Takes a dictionary containing id, update, server, and ts, then returns
        a token which is used by info_path to retrieve grabber api
        information

        Thanks to coder-alpha for the updated bitshifting obfuscation
        https://github.com/coder-alpha

        Keyword arguments:

        d -- dictionary - containing id, update, ts, server

        Returns:

        token -- integer - a unique integer
        '''
        def bitshifthex(t, e):
            i = 0
            n = 0

            for i in range(0, max(len(t), len(e))):
                if i < len(e):
                    n += ord(e[i])
                if i < len(t):
                    n += ord(t[i])

            h = format(int(hex(n),16),'x')
            return h

        def bitshiftadd(t):
            i = 0

            for e in range(0, len(t)):
                i += ord(t[e]) + e

            return i

        try:
            url = urlparse.urljoin(self.base_link, self.js_path)
            response = client.request(url)

            unpacked = jsunpack.unpack(response)

            phrase = 'function\(t,\s*i,\s*n\)\s*{\s*"use strict";\s*function e\(\)\s*{\s*return (.*?)\s*}\s*function r\(t\)'

            seed_var = re.findall(r'%s' % phrase, unpacked)[0]
            seed = re.findall(r'%s=.*?\"(.*?)\"' % seed_var, unpacked)[0]

            token = bitshiftadd(seed)

            for i in dic:
                token += bitshiftadd(bitshifthex(seed + i, dic[i]))

            return str(token)

        except Exception:
            return

    def __decode_shift(self, t, i):
        '''
        Takes a bitshifted String and removes bitshifting obfuscation

        Thanks to coder-alpha for the bitshifting algorithm
        https://github.com/coder-alpha

        Keyword arguments:

        t -- string - the obfuscated string
        i -- int -  the bitshift offset

        Returns:

        url -- string - the unobfuscated string
        '''
        try:
            n = []
            e = []
            r = ''

            for n in range(0, len(t)):
                if n == 0 and t[n] == '.':
                    pass
                else:
                    c = ord(t[n])
                    if c >= 97 and c <= 122:
                        e.append((c - 71 + i) % 26 + 97)
                    elif c >= 65 and c <= 90:
                        e.append((c - 39 + i) % 26 + 65)
                    else:
                        e.append(c)
            for ee in e:
                r += chr(ee)

            return r

        except Exception:
            return
