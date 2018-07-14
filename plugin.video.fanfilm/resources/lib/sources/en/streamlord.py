# -*- coding: utf-8 -*-

'''
    Covenant Add-on

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

from ptw.libraries import control
from ptw.libraries import cleantitle
from ptw.libraries import client
from resources.lib.libraries import jsunpack
from ptw.libraries import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['streamlord.com']
        self.base_link = 'http://www.streamlord.com'
        self.search_link = '/searchtest.php'
        self.user = control.setting('streamlord.user')
        self.password = control.setting('streamlord.pass')


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
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
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            # if (self.user != '' and self.password != ''): #raise Exception()

                # login = urlparse.urljoin(self.base_link, '/login.html')

                # post = urllib.urlencode({'username': self.user, 'password': self.password, 'submit': 'Login'})

                # cookie = client.request(login, post=post, output='cookie', close=False)

                # r = client.request(login, post=post, cookie=cookie, output='extended')

                # headers = {'User-Agent': r[3]['User-Agent'], 'Cookie': r[4]}
            # else:
                # headers = {}


            headers = {'User-Agent': client.randomagent()}
            if not str(url).startswith('http'):

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

                year = data['year']
                def searchname(r):
                    r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
                    r = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1])]
                    r = [] if r == [] else [i[0] for i in r][0]
                    return r
                
                if 'tvshowtitle' in data:
                    link = urlparse.urljoin(self.base_link, 'tvshow-%s.html' %title[0].upper())
                    r = client.request(link, headers=headers)
                    pages = dom_parser.parse_dom(r, 'span', attrs={'class': 'break-pagination-2'})
                    pages = dom_parser.parse_dom(pages, 'a', req='href')
                    pages = [(i.attrs['href']) for i in pages]
                    if pages == []:
                        r = re.findall('(watch-tvshow-.+?-\d+\.html)', r)
                        r = [(i, re.findall('watch-tvshow-(.+?)-\d+\.html', i)) for i in r]
                        r = searchname(r)
                    else:
                        for page in pages:
                            link = urlparse.urljoin(self.base_link, page)
                            r = client.request(link, headers=headers)
                            r = re.findall('(watch-tvshow-.+?-\d+\.html)', r)
                            r = [(i, re.findall('watch-tvshow-(.+?)-\d+\.html', i)) for i in r]
                            r = searchname(r)
                            if r != []: break
                else:
                    link = urlparse.urljoin(self.base_link, 'movies-%s.html' %title[0].upper())
                    r = client.request(link, headers=headers)
                    pages = dom_parser.parse_dom(r, 'span', attrs={'class': 'break-pagination-2'})
                    pages = dom_parser.parse_dom(pages, 'a', req='href')
                    pages = [(i.attrs['href']) for i in pages]
                    if pages == []:
                        r = re.findall('(watch-movie-.+?-\d+\.html)', r)
                        r = [(i, re.findall('watch-movie-(.+?)-\d+\.html', i)) for i in r]
                        r = searchname(r)
                    else:
                        for page in pages:
                            log_utils.log('shit Returned: %s' % str('in loop'), log_utils.LOGNOTICE)
                            link = urlparse.urljoin(self.base_link, page)
                            r = client.request(link, headers=headers)
                            r = re.findall('(watch-movie-.+?-\d+\.html)', r)
                            r = [(i, re.findall('watch-movie-(.+?)-\d+\.html', i)) for i in r]
                            r = searchname(r)
                            if r != []: break
                        
                    

                # leaving old search in for if streamlord renables searching on the site
                # query = urlparse.urljoin(self.base_link, self.search_link)

                # post = urllib.urlencode({'searchapi2': title})

                # r = client.request(query, post=post, headers=headers)

                # if 'tvshowtitle' in data:
                    # r = re.findall('(watch-tvshow-.+?-\d+\.html)', r)
                    # r = [(i, re.findall('watch-tvshow-(.+?)-\d+\.html', i)) for i in r]
                # else:
                    # r = re.findall('(watch-movie-.+?-\d+\.html)', r)
                    # r = [(i, re.findall('watch-movie-(.+?)-\d+\.html', i)) for i in r]

                # r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
                # r = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1])]
                # r = [i[0] for i in r][0]

                u = urlparse.urljoin(self.base_link, r)
                for i in range(3):
                    r = client.request(u, headers=headers)
                    if not 'failed' in r: break

                if 'season' in data and 'episode' in data:
                    r = re.findall('(episode-.+?-.+?\d+.+?\d+-\d+.html)', r)
                    r = [i for i in r if '-s%02de%02d-' % (int(data['season']), int(data['episode'])) in i.lower()][0]

                    r = urlparse.urljoin(self.base_link, r)

                    r = client.request(r, headers=headers)

            else:
                r = urlparse.urljoin(self.base_link, url)

                r = client.request(r, post=post, headers=headers)



            quality = 'HD' if '-movie-' in r else 'SD'

            try:
                f = re.findall('''["']sources['"]\s*:\s*\[(.*?)\]''', r)[0]
                f = re.findall('''['"]*file['"]*\s*:\s*([^\(]+)''', f)[0]

                u = re.findall('function\s+%s[^{]+{\s*([^}]+)' % f, r)[0]
                u = re.findall('\[([^\]]+)[^+]+\+\s*([^.]+).*?getElementById\("([^"]+)', u)[0]

                a = re.findall('var\s+%s\s*=\s*\[([^\]]+)' % u[1], r)[0]
                b = client.parseDOM(r, 'span', {'id': u[2]})[0]

                url = u[0] + a + b
                url = url.replace('"', '').replace(',', '').replace('\/', '/')
                url += '|' + urllib.urlencode(headers)
            except:
                try:
                    url =  r = jsunpack.unpack(r)
                    url = url.replace('"', '')
                except:
                    url = re.findall(r'sources[\'"]\s*:\s*\[.*?file[\'"]\s*:\s*(\w+)\(\).*function\s+\1\(\)\s*\{\s*return\([\'"]([^\'"]+)',r,re.DOTALL)[0][1]

            sources.append({'source': 'cdn', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False, 'autoplay': True})

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


