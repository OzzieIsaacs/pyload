# -*- coding: utf-8 -*-

import re
from builtins import _, str

import BeautifulSoup
from pyload.plugins.internal.crypter import Crypter


class DuckCryptInfo(Crypter):
    __name__ = "DuckCryptInfo"
    __type__ = "crypter"
    __version__ = "0.08"
    __pyload_version__ = "0.5"
    __status__ = "testing"

    __pattern__ = r"http://(?:www\.)?duckcrypt\.info/(folder|wait|link)/(\w+)/?(\w*)"
    __config__ = [
        ("activated", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        (
            "folder_per_package",
            "Default;Yes;No",
            "Create folder for each package",
            "Default",
        ),
    ]

    __description__ = """DuckCrypt.info decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("godofdream", "soilfiction@gmail.com")]

    TIMER_PATTERN = r'<span id="timer">(.*)</span>'

    def decrypt(self, pyfile):
        url = pyfile.url

        m = re.match(self.__pattern__, url)
        if m is None:
            self.fail(_("Weird error in link"))
        if str(m.group(1)) == "link":
            self.handle_link(url)
        else:
            self.handle_folder(m)

    def handle_folder(self, m):
        html = self.load(
            "http://duckcrypt.info/ajax/auth.php?hash={}".format(m.group(2))
        )
        m = re.match(self.__pattern__, html)
        self.log_debug("Redirect to " + m.group(0))
        html = self.load(str(m.group(0)))
        soup = BeautifulSoup.BeautifulSoup(html)
        cryptlinks = soup.findAll("div", attrs={"class": "folderbox"})
        self.log_debug("Redirect to " + cryptlinks)
        if not cryptlinks:
            self.error(_("No link found"))
        for clink in cryptlinks:
            if clink.find("a"):
                self.handle_link(clink.find("a")["href"])

    def handle_link(self, url):
        html = self.load(url)
        soup = BeautifulSoup(html)
        self.links = [soup.find("iframe")["src"]]
        if not self.links:
            self.log_info(_("No link found"))
