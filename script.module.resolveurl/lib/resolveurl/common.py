"""
    resolveurl XBMC Addon
    Copyright (C) 2011 t0mm0

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
import os
import hashlib
from lib import log_utils
from lib.net import Net, get_ua  # @UnusedImport
from lib import cache  # @UnusedImport
from lib import kodi
from lib import pyaes

logger = log_utils.Logger.get_logger()
addon_path = kodi.get_path()
plugins_path = os.path.join(addon_path, 'lib', 'resolveurl', 'plugins')
profile_path = kodi.translate_path(kodi.get_profile())
settings_file = os.path.join(addon_path, 'resources', 'settings.xml')
addon_version = kodi.get_version()
get_setting = kodi.get_setting
set_setting = kodi.set_setting
open_settings = kodi.open_settings
has_addon = kodi.has_addon
i18n = kodi.i18n

RAND_UA = get_ua()
IE_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
SMR_USER_AGENT = 'ResolveURL for Kodi/%s' % (addon_version)

def log_file_hash(path):
    try:
        with open(path, 'r') as f:
            py_data = f.read()
    except:
        py_data = ''
        
    logger.log('%s hash: %s' % (os.path.basename(path), hashlib.md5(py_data).hexdigest()))

def file_length(py_path, key=''):
    try:
        with open(py_path, 'r') as f:
            old_py = f.read()
        if key:
            old_py = encrypt_py(old_py, key)
        old_len = len(old_py)
    except:
        old_len = -1
        
    return old_len

def decrypt_py(cipher_text, key):
    if cipher_text:
        try:
            scraper_key = hashlib.sha256(key).digest()
            IV = '\0' * 16
            decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(scraper_key, IV))
            plain_text = decrypter.feed(cipher_text)
            plain_text += decrypter.feed()
            if 'import' not in plain_text:
                plain_text = ''
        except Exception as e:
            logger.log_warning('Exception during Py Decrypt: %s' % (e))
            plain_text = ''
    else:
        plain_text = ''

    return plain_text

def encrypt_py(plain_text, key):
    if plain_text:
        try:
            scraper_key = hashlib.sha256(key).digest()
            IV = '\0' * 16
            decrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(scraper_key, IV))
            cipher_text = decrypter.feed(plain_text)
            cipher_text += decrypter.feed()
        except Exception as e:
            logger.log_warning('Exception during Py Encrypt: %s' % (e))
            cipher_text = ''
    else:
        cipher_text = ''

    return cipher_text
