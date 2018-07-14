# -*- coding: utf-8 -*-

"""
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
"""

import base64
import urlparse
import urllib
import hashlib
import re,requests

from ptw.libraries import client,source_utils

def more_cdapl(link,hostDict,lang,info):
    sources = []
    if "cda.pl" in link:
        try:
            response = requests.get(link).content
            test = client.parseDOM(response, 'div', attrs={'class':'wrapqualitybtn'})
            urls = client.parseDOM(test, 'a', ret='href')
            for url in urls:
                valid, host = source_utils.is_host_valid(url, hostDict)
                q = source_utils.check_sd_url(url)
                direct = re.findall("""file":"(.*)","file_cast""", requests.get(url).content)[0].replace("\\/","/")
                sources.append({'source': host, 'quality': q, 'language': lang, 'url': direct, 'info': info, 'direct': True, 'debridonly': False})
            return sources
        except Exception,e:
            print e
            return []
    return []
def more_rapidvideo(link,hostDict,lang,info):
    sources = []
    if "rapidvideo.com" in link:
        try:
            response = requests.get(link).content
            test = re.findall("""(https:\/\/www.rapidvideo.com\/e\/.*)">""", response)
            numGroups = len(test)
            for i in range(1,numGroups):
                url = test[i]
                valid, host = source_utils.is_host_valid(url, hostDict)
                q = source_utils.check_sd_url(url)
                sources.append({'source': host, 'quality': q, 'language': lang, 'url': url, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except Exception,e:
            print e
            return []
    return []
