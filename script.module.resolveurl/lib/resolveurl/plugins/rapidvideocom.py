# -*- coding: utf-8 -*-
"""
resolveurl XBMC Addon
Copyright (C) 2011 t0mm0

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
"""
from __resolve_generic__ import ResolveGeneric
import requests

class RapidVideoResolver(ResolveGeneric):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com", "raptu.com", "bitporno.com"]
    pattern = '(?://|\.)((?:rapidvideo|raptu|bitporno)\.com)/(?:[ev]/|embed/|\?v=)?([0-9A-Za-z]+)'

    def get_url(self, host, media_id):
        content = requests.get(self._default_get_url(host, media_id, template='https://{host}/embed/{media_id}')).content
        if "&q=1080p" in content:
            return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}&q=1080p')
        if "&q=720p" in content:
            return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}&q=720p')
        if "&q=480p" in content:
            return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}&q=480p')
        if "&q=360p" in content:
            return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}&q=360p')
