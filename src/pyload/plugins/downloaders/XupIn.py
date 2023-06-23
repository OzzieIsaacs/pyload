# -*- coding: utf-8 -*-

import json
import re
import pycurl
from ..base.xfs_downloader import XFSDownloader
from base64 import standard_b64decode

# from bs4 import BeautifulSoup

class XupIn(XFSDownloader):
    __name__ = "XupIn"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(www\.)?xup\.in/dl,.*"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Xup.In downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "xup.in"

    NAME_PATTERN = r'<div class="name position-relative">\s*<h4>(?P<N>.+?)</h4>'
    SIZE_PATTERN = r'<span class="file-size">(?P<S>[\d.,]+) (?P<U>[\w^_]+)</span>'

    OFFLINE_PATTERN = r"<h4>File Not Found</h4>"
    DL_LIMIT_PATTERN = r"You have to wait (.+?) till next download"

    API_KEY = "37699zuaj90n9hxado2m7"
    API_URL = "https://api-v2.ddownload.com/api/"

    def process(self, pyfile):
        site = self.load(pyfile.url)
        html = re.search('var zdec = "(.*)";', site)
        if html:
            decoded = standard_b64decode(html.group(1)).decode('iso-8859-1')
            vid = re.search(r'<input type="hidden" value="(.*)" name="vid"', decoded)
            vtime = re.search(r'<input type="hidden" value="(\d+)" name="vtime"', decoded)
            link = re.search(r'<form action="(.*)" method="post">', decoded)
            name = re.search(r'<h1 itemprop="headline">Download:\s(.*)</h1>\s</legend>', decoded)
            wait = re.search(r'<li class="nolist"><input size="1" value="(\d+)" id="xupctr" />', decoded)
            self.pyfile.name = name.group(1)
            self.wait(wait.group(1))

            self.download("https:" + link.group(1), post={"vid":vid.group(1), "vtime":vtime.group(1)})



'''
Knopf zum übetragen
value="4" -> bedeutet 4 Sekunden warten
<li class="nolist"><input size="1" value="4" id="xupctr" /> <button type="submit" class="upbut" id="ddl"> <b>Download</b> </button></li>

# Dateigröße
<li class="iclist">File Size: 0.62 Mbyte</li>

# Dateiname
<legend> <h1 itemprop="headline">Download: fvgvtzguhnuijnujp.rar</h1> </legend>


Durch Druck auf den Knopf gibt es ein :

https://www1.xup.in/exec/xddl.php?fid=18041049&fname=fvgvtzguhnuijnujp.rar&uid=0&key=

mit folgenden Daten: vid=v131612a547f4e165142f56af4b2bd7e77&vtime=1687513933

Findet man im html unter:
<form action="//www1.xup.in/exec/xddl.php?fid=18041049&fname=fvgvtzguhnuijnujp.rar&uid=0&key=" method="post">
<input type="hidden" value="v1a238a34ae2a9a407e33b149b280e0b41" name="vid" />
<input type="hidden" value="1687512526" name="vtime" />
'''