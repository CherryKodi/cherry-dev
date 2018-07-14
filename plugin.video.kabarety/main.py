# -*- coding: UTF-8 -*-
import urllib, urllib2, re, xbmc, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, os
import requests
from ptw.libraries import source_utils, dom_parser, client, cleantitle
import resolveurl
import sys

reload(sys)
sys.setdefaultencoding('utf8')

#=########################################################################################################=#
#                                                   MENU                                                   #
#=########################################################################################################=#
def CATEGORIES():
    #addDir("Szukaj", '', 1, '','','', True)
    addDir("Najpopularniejsze", '', 2, '','','', True)
    addDir("Wszystkie", '', 3, '','','', True)

###################################################################################
#=########################################################################################################=#
#                                                 FUNCTIONS                                                #
#=########################################################################################################=#
def mySearch():
    keyb = xbmc.Keyboard('', "Wyszukiwarka kreskówek")
    keyb.doModal()
    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0 :
        search = keyb.getText()
        myParam = str(urllib.quote(search)).strip()
        url = "http://www.kreskowkazone.pl/szukaj?szukana="+search
        r = client.request(url)
        result = client.parseDOM(r, 'div', attrs={'class':'box-img'})
        linki = client.parseDOM(result, 'a', ret='href')
        if len(linki) == 0:
            addDir("Zbyt dużo lub brak wyników wyszukiwania :(", '', None, 'ikona.png','thumb.png',None, True)
            addDir("Spróbuj doprecyzować zapytanie!", '', None, 'ikona.png','thumb.png',None, True)
        nazwy = client.parseDOM(result, 'a')
        nazwy = client.parseDOM(nazwy, 'img', ret='alt')
        
        counter = 0
        for link in linki:
            linki[counter] = 'http://www.kreskowkazone.pl/' + str(link)
            addDir(str(nazwy[counter]), linki[counter], 4, 'ikona.png','thumb.png',None, True)
            counter+=1   
    else:
        CATEGORIES()
    
def myOther():
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('XBMC', 'Hello World')
    
def addDir(name, url, mode, iconimage, thumb, opis, isFolder=True, total=1):
    u=sys.argv[0]+'?url='+urllib.quote_plus(url)+'&mode='+str(mode)+'&name='+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconimage, thumbnailImage=thumb)
    url = thumb
    liz.setArt({'thumb': thumb,
                'icon': iconimage,
                'fanart': url})
    liz.setInfo("Video", {'title':name , 'genre':'', 'rating': 0, 'plot': opis})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok

def work(item):
    nazwa = str(client.parseDOM(item, 'p')[0])
    link = str(client.parseDOM(item, 'a', ret='href')[0])
    r = client.request("http://kabaret.tworzymyhistorie.pl" + link)
    result = client.parseDOM(r, 'div', attrs={'class':'site_skecze'})
    kategoria=str(client.parseDOM(result, 'span', ret='name')[0])
    link = str(kategoria)
    return (nazwa,link)

def Najpopularniejsze():
    Najpopularniejsze_Lista = [('Kabaret Skeczów Męczących', '65'), ('Kabaret Moralnego Niepokoju', '47'), ('Kabaret Młodych Panów', '46'), ('Kabaret Paranienormalni', '57'), ('Kabaret Neo-Nówka', '50'), ('Kabaret Ani Mru-Mru', '23'), ('Kabaret Smile', '67'), ('Kabaret Nowaki', '127'), ('Kabaret Limo', '43'), ('Kabaret Łowcy.B', '101'), ('Kabaret Hrabi', '37'), ('Kabaret Jurki', '38'), ('Kabaret Pod Wyrwigroszem', '61'), ('Kabaret OT.TO', '56'), ('Formacja Chatelet', '5'), ('Spadkobiercy', '111'), ('Cezary Pazura', '4'), ('Kabaretowy Klub Dwójki', '225'), ('Festiwale kabaretowe', '229'), ('Piotr Bałtroczyk', '91')]
    url = 'http://kabaret.tworzymyhistorie.pl/kabarety/'
    r = client.request(url)
    result = client.parseDOM(r, 'div', attrs={'class':'rborder'})[0]
    result = client.parseDOM(result, 'div', attrs={'class':'kat_lista'})
    nazwy = []
    linki = []
    kategorie = []
    results = Najpopularniejsze_Lista
    for item in results:
        addDir(item[0], item[1], 4, 'ikona.png','thumb.png',None, True)

def Wszystkie():
    Wszystkie_Lista = [('Abelard Giza', '244'), ('Adam Van Bendler', '290'), ('Akademia Rozrywki', '202'), ('Alosza Awdiejew', '227'), ('Andrzej Grabowski', '1'), ('Andrzej Poniedzielski', '2'), ('Antoni Gorgoń-Grucha', '289'), ('Antoni Syrek-Dąbrowski', '250'), ('Artur Andrus', '3'), ('Bartek Walos', '253'), ('Bartosz Gajda', '288'), ('Bartosz Zalewski', '281'), ('Cezary Jurkiewicz', '239'), ('Cezary Pazura', '4'), ('Co leci w sieci', '254'), ('Comedy Central Prezentuje Stand Up', '193'), ('Comedy Menshow', '255'), ('Dasza Von Yock', '126'), ('Dzięki Bogu już weekend', '247'), ('Ewa Błachnio', '263'), ('Fair Play Crew', '259'), ('Festiwale kabaretowe', '229'), ('Filharmonia Dowcipu', '98'), ('Formacja Chatelet', '5'), ('Formacja Kompania Grabi', '34'), ('Formacja Legitymacje', '6'), ('Genowefa Pigwa', '268'), ('Grupa AD HOC', '217'), ('Grupa Inicjatyw Teatralnych', '7'), ('Grupa MoCarta', '8'), ('Grupa Rafała Kmity', '11'), ('Grupy Impro', '232'),('Grzegorz Halama', '12'),('HBO - Stand Up Comedy Club', '189'),('Hu jak humor', '194'),('I kto to mówi?', '246'),('Ipkis', '279'),('Ireneusz Krosny', '13'),('Ja Mmm Chyba Ściebie', '118'),('Jacek Fedorowicz', '14'),('Jacek Noch', '272'),('Jacek Stramik', '283'),('Jacek Ziobro', '15'),('Jan Pietrzak', '277'),('Jan Tadeusz Stanisławski', '17'),('Janusz Gajos', '18'),('Janusz Rewiński', '19'),('Jerzy Kryszak', '20'),('Jerzy Stuhr', '143'),('Jim Williams', '240'),('Joanna Jeżewska', '21'),('Kabaret 3D', '149'),('Kabaret 44-200', '237'),('Kabaret 7 minut Po', '234'),('Kabaret Adin', '117'),('Kabaret Afera', '22'),('Kabaret Ancla', '249'),('Kabaret Ani Mru-Mru', '23'),('Kabaret Babeczki z Rodzynkiem', '24'),('Kabaret Bartki', '142'),('Kabaret Bes Szans', '175'),('Kabaret BudaPesz', '274'),('Kabaret Cegła', '25'),('Kabaret Chwilowo Kaloryfer', '26'),('Kabaret Chyba', '153'),('Kabaret Ciach', '27'),('Kabaret Czesuaf', '28'),('Kabaret Członek Polski', '163'),('Kabaret Czołówka Piekła', '273'),('Kabaret Czwarta Fala', '157'),('Kabaret Dabz', '144'),('Kabaret DKD', '29'),('Kabaret Długi', '30'),('Kabaret Dno', '31'),('Kabaret Dudek', '32'),('Kabaret Dworski', '204'),('Kabaret Elita', '33'),('Kabaret Hi Fi (Halama, Kamys)', '35'),('Kabaret Hlynur', '36'),('Kabaret Hrabi', '37'),('Kabaret Huć', '187'),('Kabaret Inaczej', '168'),('Kabaret Inni Inaczej', '154'),('Kabaret Inteligentny', '132'),('Kabaret IPN', '114'),('Kabaret Jurki', '38'),('Kabaret K2', '233'),('Kabaret Kałamasz', '216'),('Kabaret Kałasznikof', '39'),('Kabaret Klakier', '113'),('Kabaret Klinkiernia', '40'),('Kabaret Koń Polski', '41'),('Kabaret Kuzyni', '42'),('Kabaret Limo', '43'),('Kabaret Łowcy.B', '101'),('Kabaret Macież', '125'),('Kabaret Made in China', '45'),('Kabaret Masakra', '155'),('Kabaret Mimika', '172'),('Kabaret Młodych Panów', '46'),('Kabaret Moralnego Niepokoju', '47'),('Kabaret Mumio', '48'),('Kabaret Na Koniec Świata', '265'),('Kabaret Napad', '49'),('Kabaret Neo-Nówka', '50'),('Kabaret Nic nie szkodzi', '138'),('Kabaret Nie My', '221'),('Kabaret Niepoprawnych Optymistów', '257'),('Kabaret NOC', '129'),('Kabaret Noł Nejm', '51'),('Kabaret Non-Sens', '52'),('Kabaret Nowaki', '127'),('Kabaret Olgi Lipińskiej', '54'),('Kabaret OTOoni', '55'),('Kabaret OT.TO', '56'),('Kabaret Paralaksa', '178'),('Kabaret Paranienormalni', '57'),('Kabaret PiC', '162'),('Kabaret Pirania', '58'),('Kabaret Po Żarcie', '59'),('Kabaret Pod Bańką', '208'),('Kabaret Pod Egidą', '60'),('Kabaret Pod Grzybem', '133'),('Kabaret Pod Napięciem', '236'),('Kabaret Pod Wyrwigroszem', '61'),('Kabaret Poszukiwani', '148'),('Kabaret Potem', '62'),('Kabaret PUK', '121'),('Kabaret Rak', '63'),('Kabaret Rewers', '260'),('Kabaret Róbmy Swoje', '190'),('Kabaret Sakreble', '64'),('Kabaret Skeczów Męczących', '65'),('Kabaret Słuchajcie', '66'),('Kabaret Smile', '67'),('Kabaret Snobów', '151'),('Kabaret Starszych Panów', '68'),('Kabaret Statyf', '69'),('Kabaret Stonka Ziemniaczana', '165'),('Kabaret Świerszczychrząszcz', '73'),('Kabaret Szarpanina', '173'),('Kabaret Szum', '70'),('Kabaret Szydera', '124'),('Kabaret Taleja', '112'),('Kabaret Tenor', '72'),('Kabaret Tera Jem', '161'),('Kabaret Tey (Laskowik)', '74'),('Kabaret TIRURIRU', '222'),('Kabaret To Za Duże Słowo', '103'),('Kabaret Trzecia Strona Medalu', '261'),('Kabaret Ucho', '131'),('Kabaret Weźrzesz', '186'),('Kabaret Widelec', '76'),('Kabaret Ymlałt', '158'),('Kabaret z Konopi', '77'),('Kabaret Z Nazwy', '78'),('Kabaret Zachodni', '264'),('Kabaret Zażarty', '79'),('Kabaret Zwiększonego Ryzyka', '160'),('Kabaret Zygzak', '120'),('Kabaretowy Klub Dwójki', '225'),('Kabaretowy Klub Kanapowy', '251'),('Kabaretożercy (teleturniej)', '174'),('Kabaretus Fraszka', '206'),('Kabarety zza kulis', '198'),('Kacper Ruciński', '141'),('Kaczka Pchnięta Nożem', '180'),('Karol Kopiec', '243'),('Karol Modzelewski', '280'),('Katarzyna Pakosińska', '248'),('Katarzyna Piasecka', '136'),('Kevin Aiston', '80'),('Krzesło Wuja Tobiasza', '135'),('Krzysztof Daukszewicz', '81'),('Krzysztof Piasecki', '82'),('Kabarety', '286'),('Kwartet Okazjonalny', '83'),('Latajacy Klub Dwójki', '256'),('Leszek Lichota', '150'),('Liquidmime', '171'),('Łukasz Błąd', '140'),('Łukasz Kaczmarczyk', '287'),('Łukasz Lotek Lodkowski', '267'),('Maciej Stuhr', '84'),('Magda Mleczak', '85'),('Mann i Materna', '86'),('Marcin Daniec', '87'),('Marcin Wojciech', '235'),('Marek Grabie', '241'),('Marek Majewski', '88'),('Marian Opania', '89'),('Michał Kempa', '210'),('Narwani z Kontekstu', '275'),('Olka Szczęśniak', '284'),('Paweł Dłużewski', '90'),('Paweł Reszela', '203'),('Piotr Bałtroczyk', '91'),('Piotr Bukartyk', '215'),('Projekt Kwiaty', '116'),('Pyda Squad', '146'),('Rafał Pacześ', '276'),('Rafał Rutkowski', '242'),('Rodzina Trendych', '184'),('Ryszard Makowski', '92'),('Ścibor Szpak', '102'),('Sebastian Rejent', '270'),('Sekcja Muzyczna Kołłątajowskiej Kuźni Prawdziwych Mężczyzn', '258'),('Siedem Razy Jeden', '231'),('Sławomir', '282'),('Słoiczek po cukrze', '119'),('Spadkobiercy', '111'),('Stado Umtata', '122'),('Stanisław Tym', '93'),('Steffen Möller', '94'),('Szymon Jachimek', '262'),('Szymon Łątkowski', '266'),('Tadeusz Drozda', '137'),('Tadeusz Ross', '96'),('Teatr Montownia', '152'),('Tercet czyli Kwartet', '213'),('The Umbilical Brothers', '200'),('Tomasz Boras', '285'),('Tomasz Jachimek', '16'),('Tomasz Nowaczyk', '245'),('Tomek Biskup', '269'),('Trzeci Oddech Kaczuchy', '97'),('Tylko dla dorosłych', '238'),('Ucho Prezesa', '278'),('Wojciech Młynarski', '164'),('Wojtek Fiedorczuk', '271'),('Wspólne występy', '167'),('Wytwórnia AYOY', '99'),('Za chwilę dalszy ciąg programu', '130'),('Zabij Mnie Śmiechem', '176'),('Zaczynam kabaret', '223'),('Zagraniczne Kabarety', '170')]
    url = 'http://kabaret.tworzymyhistorie.pl/kabarety/'
    r = client.request(url)
    result = client.parseDOM(r, 'div', attrs={'class':'rborder'})[1]
    result = client.parseDOM(result, 'div', attrs={'class':'kat_lista'})
    nazwy = []
    linki = []
    kategorie = []
    results = Wszystkie_Lista
    for item in results:
        addDir(item[0], item[1], 4, 'ikona.png','thumb.png',None, True)

def Listowanie_Odcinkow():
    url = urllib.unquote_plus(params['url'])
    s = requests.Session()
    s.get("http://kabaret.tworzymyhistorie.pl/kabarety/")
    
    headers = {
    'Host': 'kabaret.tworzymyhistorie.pl',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Accept': '*/*',
    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
    'Referer': 'http://kabaret.tworzymyhistorie.pl/kabarety/',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    }
    
    parametry = (
        ('tod', 'skecze_lista'),
        ('cat', url),
        ('typ', '0'),
        ('title', ''),
        ('sort', 'id'),
        ('order', 'desc'),
        ('limit', '0'),
        ('count', '2000'),
    )
    
    test = s.get('http://kabaret.tworzymyhistorie.pl/index/exec/load.php', headers=headers, params=parametry, cookies=s.cookies)
    r = test.content
    linki = client.parseDOM(r, 'a', ret='href')
    nazwy = client.parseDOM(r, 'img', ret='alt')
    from collections import OrderedDict
    linki = OrderedDict((x, True) for x in linki).keys()
    for item in zip(linki,nazwy):
        link = "http://kabaret.tworzymyhistorie.pl/" + item[0]
        nazwa = item[1]
        if "tvp" in str(nazwa).lower():
            continue
        addDir(str(nazwa), str(link), 5, 'ikona.png','thumb.png',None, False)

def Wyciaganie_Linkow():
    url = urllib.unquote_plus(params['url'])
    url = urllib.unquote(url)
    r = client.request(url)
    video_link = str(client.parseDOM(r, 'iframe', ret='src')[0])
    video_link = resolveurl.resolve(video_link)
    xbmc.Player().play(str(video_link))

    
###################################################################################
#=########################################################################################################=#
#                                               GET PARAMS                                                 #
#=########################################################################################################=#    
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2 :
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/') :
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)) :
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

params = get_params()
url = None
name = None
mode = None
iconimage = None

try:
    url = urllib.unquote_plus(params['url'])
except:
    pass
try:
    name = urllib.unquote_plus(params['name'])
except:
    pass
try:
    mode = int(params['mode'])
except:
    pass
try:        
    iconimage = urllib.unquote_plus(params['iconimage'])
except:
    pass


        
###################################################################################
#=###########################################################################################################=#
#                                                   MODES                                                     #
#=###########################################################################################################=#
if mode == None :
    CATEGORIES()
elif mode == 1 :
    mySearch()
elif mode == 2 :
    Najpopularniejsze()
elif mode == 3 :
    Wszystkie()
elif mode == 4 :
    Listowanie_Odcinkow()
elif mode == 5 :
    Wyciaganie_Linkow()
elif mode == 6 : 
    url = urllib.unquote_plus(params['url'])
    url = resolveurl.resolve(url)
    xbmc.Player().play(str(url))
    
###################################################################################
xbmcplugin.endOfDirectory(int(sys.argv[1]))