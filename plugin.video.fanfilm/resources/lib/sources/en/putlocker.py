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


import re,urllib,urlparse,json,base64,time,xbmc

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import cache
from resources.lib.libraries import directstream
from resources.lib.libraries import source_utils



class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['putlocker.systems', 'putlocker-movies.tv', 'cartoonhd.website', 'cartoonhd.online', 'cartoonhd.cc', 'cartoonhd.life','cartoonhd.zone']
        self.base_link = 'https://cartoonhd.io'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
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
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def searchShow(self, title, season, episode, aliases, headers):
        try:
            for alias in aliases:
                url = '%s/show/%s/season/%01d/episode/%01d' % (self.base_link, cleantitle.geturl(title), int(season), int(episode))
                url = client.request(url, headers=headers,output='geturl', timeout='10')
                if not url == None and url != self.base_link: break
            return url
        except:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            for alias in aliases:
                url = '%s/full-movie/%s' % (self.base_link, cleantitle.geturl(alias['title']))
                url = client.request(url, headers=headers, output='geturl', timeout='10')
                if not url == None and url != self.base_link: break
            if url == None:
                for alias in aliases:
                    url = '%s/full-movie/%s-%s' % (self.base_link, cleantitle.geturl(alias['title']), year)
                    url = client.request(url, headers=headers, output='geturl', timeout='10')
                    if not url == None and url != self.base_link: break

            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            imdb = data['imdb']
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                url = self.searchShow(title, int(data['season']), int(data['episode']), aliases, headers)
            else:
                url = self.searchMovie(title, data['year'], aliases, headers)

            r = client.request(url, headers=headers, output='extended', timeout='10')

            if not imdb in r[0]: raise Exception()

            cookie = r[4] ; headers = r[3] ; result = r[0]

            try:
                r = re.findall('(https:.*?redirector.*?)[\'\"]', result)
                for i in r:
                    try:
                        sources.append(
                            {'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en',
                             'url': i, 'direct': True, 'debridonly': False})
                    except:
                        pass
            except:
                pass

            try: auth = re.findall('__utmx=(.+)', cookie)[0].split(';')[0]
            except: auth = 'false'
            auth = 'Bearer %s' % urllib.unquote_plus(auth)
            headers['Authorization'] = auth
            headers['Referer'] = url

            u = '/ajax/vsozrflxcw.php'
            self.base_link = client.request(self.base_link, headers=headers, output='geturl')
            u = urlparse.urljoin(self.base_link, u)

            action = 'getEpisodeEmb' if '/episode/' in url else 'getMovieEmb'

            elid = urllib.quote(base64.encodestring(str(int(time.time()))).strip())

            token = re.findall("var\s+tok\s*=\s*'([^']+)", result)[0]

            idEl = re.findall('elid\s*=\s*"([^"]+)', result)[0]

            post = {'action': action, 'idEl': idEl, 'token': token, 'nopop': '', 'elid': elid}
            post = urllib.urlencode(post)
            cookie += ';%s=%s'%(idEl,elid)
            headers['Cookie'] = cookie

            r = client.request(u, post=post, headers=headers, cookie=cookie, XHR=True)
            r = str(json.loads(r))

            r = re.findall('\'(http.+?)\'', r) + re.findall('\"(http.+?)\"', r)

            for i in r:
                try:
                    if 'google' in i:
                        quality = 'SD'

                        if 'googleapis' in i:
                            try:
                                quality = source_utils.check_sd_url(i)
                            except Exception:
                                pass

                        if 'googleusercontent' in i:
                            i = directstream.googleproxy(i)
                            try:
                                quality = directstream.googletag(i)[0]['quality']
                            except Exception:
                                pass

                        sources.append({
                            'source': 'gvideo',
                            'quality': quality,
                            'language': 'en',
                            'url': i,
                            'direct': True,
                            'debridonly': False
                        })

                    elif 'llnwi.net' in i or 'vidcdn.pro' in i:
                        try:
                            quality = source_utils.check_sd_url(i)

                            sources.append({
                                'source': 'CDN',
                                'quality': quality,
                                'language': 'en',
                                'url': i,
                                'direct': True,
                                'debridonly': False
                            })

                        except Exception:
                            pass

                    else:
                        valid, hoster = source_utils.is_host_valid(i, hostDict)

                        sources.append({
                            'source': hoster,
                            'quality': '720p',
                            'language': 'en',
                            'url': i,
                            'direct': False,
                            'debridonly': False
                        })

                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        if 'google' in url and not 'googleapis' in url:
            return directstream.googlepass(url)
        else:
            return url
