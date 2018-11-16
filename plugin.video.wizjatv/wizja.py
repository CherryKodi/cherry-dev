# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals, print_function

import json
import re
import urllib

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

import xbmcaddon
from ptw.debug import log_exception, log
from ptw.libraries import client


class WizjaTvApi:

    def __init__(self):
        self.MAIN_URL = 'http://wizja.tv/'
        self.DEFAULT_ICON_URL = 'http://wizja.tv/logo.png'
        self.HTTP_HEADER = {'User-Agent': 'Mozilla/5.0', 'Accept': 'text/html'}
        self.login = xbmcaddon.Addon().getSetting('user')
        self.password = xbmcaddon.Addon().getSetting('pass')

        self.http_params = {}
        self.http_params.update(
            {'header': self.HTTP_HEADER})
        self.loggedIn = False

    def doLogin(self, login, password, s):
        logged = False
        premium = False
        loginUrl = 'http://wizja.tv/users/index.php'

        HTTP_HEADER = dict(self.HTTP_HEADER)
        HTTP_HEADER.update({'Referer': loginUrl})
        params = dict(self.http_params)
        params['header'] = HTTP_HEADER

        post_data = {'user_name': login, 'user_password': password, 'login': 'Zaloguj'}
        data = self.postUrlRequestData(loginUrl, s, post_data)
        data = data.text
        # log data
        if data:
            if '?logout' in data:
                log('WizjaTvApi.doLogin login as [%s]' % login)
                logged = True
                if 'Premium aktywne do ' in data:
                    premium = True
            else:
                log('WizjaTvApi.doLogin login failed - wrong user or password? %s' % login)
        return logged, premium

    def getList(self):
        log("WizjaTvApi.getChannelsList")
        import requests
        s = requests.Session()
        if self.login != '' and self.password != '':
            ret = self.doLogin(self.login, self.password, s)
            if ret[0]:
                self.loggedIn = True
                if not ret[1]:
                    log('Użytkownika "%s" zalogowany poprawnie. Brak premium!' % login)
                    return []
            else:
                log('Problem z zalogowanie użytkownika "%s". Sprawdź dane do logowania w konfiguracji hosta.' % login)
                self.loggedIn = False
                return []
        else:
            log(
                'Serwis ten wymaga zalogowania. Wprowadź swój login i hasło w konfiguracji hosta dostępnej po naciśnięciu niebieskiego klawisza.')
            return []

        channelsTab = []

        data = self.getUrlRequestData("http://wizja.tv/", s)
        data = client.parseDOM(data.text, 'ul', attrs={'class': 'dropdown-menu'})[0]
        linki = client.parseDOM(data, 'a', ret='href')
        ikony = client.parseDOM(data, 'img', ret='src')
        for tuple in zip(linki, ikony):
            icon = str("http://wizja.tv/" + tuple[1])
            url = str("http://wizja.tv/" + tuple[0])
            title = icon.split('/')[-1][:-4].upper()

            params = {'name': 'wizja.tv',
                      'type': 'video',
                      'title': title,
                      'url': url,
                      'icon': icon}
            channelsTab.append(params)

        return s, channelsTab

    def getVideoLink(self, url, s):
        log("WizjaTvApi.getVideoLink")
        urlsTab = []

        data = s.get(url).content
        data = client.parseDOM(data, 'iframe', ret='src')
        log("WizjaTvApi." + str(data))
        for url in data:
            HTTP_HEADER = dict(self.HTTP_HEADER)
            HTTP_HEADER.update({'Referer': url})
            params = dict(self.http_params)
            params['header'] = HTTP_HEADER

            tries = 0
            while tries < 2:
                tries += 1

                if 'porter' in url or 'player' in url:
                    tmp = s.get("http://wizja.tv/" + url).text
                    videoUrl = re.search('src: "(.*?)"', tmp)
                    try:
                        videoUrl = videoUrl.group(1)
                        videoUrl = urllib.unquote(videoUrl).decode('utf8')
                    except:
                        log_exception()
                        videoUrl = ''
                    killUrl = re.search("""<a href="(.*?)" target="_top">Z""", tmp)
                    try:
                        killUrl = killUrl.group(1)
                        killUrl = urllib.unquote(killUrl).decode('utf8')
                    except:
                        log_exception()
                        killUrl = ''
                    if videoUrl != '':
                        urlTab = re.search("""rtmp:\/\/([^\/]+?)\/([^\/]+?)\/([^\/]+?)\?(.+?)&streamType""",
                                           str(videoUrl))
                        xbmc_rtmp = 'rtmp://' + urlTab.group(1) + '/' + urlTab.group(
                            2) + '?' + urlTab.group(4) + \
                                    ' app=' + urlTab.group(2) + '?' + urlTab.group(4) + \
                                    ' playpath=' + urlTab.group(3) + '?' + urlTab.group(4) + \
                                    ' swfVfy=1 flashver=LNX\\25,0,0,12 timeout=25 ' \
                                    'swfUrl=https://wizja.tv/player/StrobeMediaPlayback_v5.swf live=0 ' \
                                    'pageUrl=https://wizja.tv/' + str(url).replace("porter.php?ch", "watch.php?id")
                        urlsTab.append({'name': 'rtmp', 'url': xbmc_rtmp})
                    else:
                        s.get("http://wizja.tv/" + killUrl)
                        continue
                break
        return urlsTab

    def ListaKanalow(self):
        try:
            s, channelList = self.getList()
        except:
            log_exception()
            return ''
        if len(channelList) < 2:
            return ''
        else:
            return s, json.dumps(channelList)

    def Link(self, url, s):
        wynik = ''
        try:
            link = self.getVideoLink(url, s)
            wynik = link[0]['url']
        except:
            log_exception()
        return str(wynik)

    @staticmethod
    def getUrlRequestData(url, s, proxy=False):
        proxyDict = {
            "http": "66.70.147.195:3128",
        }
        if proxy:
            log("WizjaTvApi.Proxy = True")
            log("WizjaTvApi.ProxyIP: " + str(proxyDict))
            r = s.get(url, proxies=str(proxyDict))
            return r
        else:
            r = s.get(url)
            return r

    @staticmethod
    def postUrlRequestData(url, s, data, proxy=False):
        proxyDict = {
            "http": "66.70.147.195:3128",
        }
        if proxy:
            log("WizjaTvApi.Proxy = True")
            log("WizjaTvApi.ProxyIP: " + str(proxyDict))
            r = s.post(url, data=data, proxies=proxyDict)
            return r
        else:
            r = s.post(url, data=data)
            return r
