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

import re,urllib,urlparse,httplib,json,xbmc

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import directstream
from resources.lib.libraries import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['seriesonline.io', 'www1.seriesonline.io', 'series9.io']
        self.base_link = 'https://www1.series9.io'
        self.search_link = '/movie/search/%s'
        self.api_link = 'https://api.yesmovie.io/series/ajax/suggest_search?keyword=%s&img=//cdn.themovieseries.net/&link_web=https://www1.series9.io/'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

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

    def searchShow(self, title, season, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            search = '%s Season %d' % (title, int(season))
            url = self.api_link % cleantitle.geturl(search)
            r = client.request(url)
            r = json.loads(r)['content']
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', attrs={'class': 'ss-title'}))
            url = [i[0] for i in r if cleantitle.get(search) == cleantitle.get(i[1])][0]

            return url
        except:
            return

    def searchMovie(self, title, year, aliases, headers):
        try:
            title = cleantitle.normalize(title)
            url = self.api_link % cleantitle.geturl(title)
            r = client.request(url)
            r = json.loads(r)['content']
            r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', attrs={'class': 'ss-title'}))
            url = [i[0] for i in r if cleantitle.get(title) == cleantitle.get(i[1])][0]
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)

            else:
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            if url == None: raise Exception()

            r = client.request(url)
            r = client.parseDOM(r, 'div', attrs={'class': 'les-content'})

            if 'tvshowtitle' in data:
                ep = data['episode']
                links = client.parseDOM(r, 'a', attrs={'episode-data': ep}, ret='player-data')
            else:
                links = client.parseDOM(r, 'a', ret='player-data')

            for link in links:
                if 'vidnode.net' in link:
                    try:
                        files = []
                        while True:
                            try:
                                try:r = client.request(link)
                                except: continue

                                files.extend(re.findall("{file: \'(.+?)\',label: \'(.+?)\'.+?}", r))

                                link = re.findall('window\.location = \"(.+?)\";', r)[0]

                                if not 'vidnode' in link:
                                    break

                            except Exception:
                                break

                        for i in files:
                            try:
                                url = i[0]
                                quality = i[1]
                                host = 'CDN'

                                if 'google' in url:
                                    host = 'gvideo'

                                    if 'lh3.googleusercontent.com' in url:
                                        url = directstream.googleproxy(url)

                                sources.append({
                                    'source': host,
                                    'quality': source_utils.label_to_quality(quality),
                                    'language': 'en',
                                    'url': url,
                                    'direct': True,
                                    'debridonly': False
                                })
                            except:
                                pass
                    except:
                        pass
                else:
                    try:
                        host = urlparse.urlparse(link.strip().lower()).netloc

                        if not host in hostDict: raise Exception()

                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')

                        sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': link, 'direct': False, 'debridonly': False})
                    except:
                        pass

            return sources
        except:
            return sources


    def resolve(self, url):
        if "google" in url:
            return directstream.googlepass(url)
        else:
            return url
