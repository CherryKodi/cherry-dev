'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import re, requests, xbmc
from lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError

class FreediscResolver(ResolveUrl):
    name = "freedisc"
    domains = ["freedisc.pl"]
    pattern = "(?://|\.)(freedisc\.(?:pl))/.*/([a-zA-Z0-9]+)"

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        s = requests.session()
        web_url = self.get_url(host, media_id)
        UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
        headers = {'User-Agent': UA, 'Referer': web_url}
        s.headers.update(headers)
        html = s.get(web_url, headers=headers).content
        cookie = s.cookies.get_dict()
        cookie_string = "; ".join([str(x) + "=" + str(y) for x, y in cookie.items()])
        cookie = {'cookie': cookie_string,
                'dnt': '1',
                'accept-encoding': 'identity;q=1, *;q=0',
                'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'user-agent': UA,
                'accept': '*/*',
                'authority': 'stream.freedisc.pl',
                'range': 'bytes=0-',}
        s.headers.update(cookie)
        url = re.findall("""video_src.*href=\"http.*?file=(.*)\"""", html)[0]
        
        out = url + helpers.append_headers(s.headers)
        if out:
            return out
        raise ResolverError('Video not found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://freedisc.pl/embed/video/{media_id}')
