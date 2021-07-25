# -*- coding: utf-8 -*-
import re

from ..base.decrypter import BaseDecrypter


class SexuriaNet(BaseDecrypter):
    __name__ = "SexuriaNet"
    __type__ = "decrypter"
    __version__ = "0.16"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?sexuria\.net/\d+-(?P<N>.+)\.html"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_subfolder", "bool", "Save package to subfolder", True),
        (
            "folder_per_package",
            "Default;Yes;No",
            "Create folder for each package",
            "Default",
        ),
    ]

    __description__ = """Sexuria.net decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("NETHead", "NETHead.AT.gmx.DOT.net")]

    PATTERN_TITLE = r"<h1>(?P<TITLE>.*)</h1>"
    PATTERN_REDIRECT_LINKS = r'<a target="_blank" href="(.*?)">' # 'disabled\'" href="(.*)" id'


    def decrypt(self, pyfile):
        #: Init
        self.pyfile = pyfile
        self.package = pyfile.package()

        #: Decrypt and add links
        pack_name, self.urls, folder_name = self.decrypt_links(
            self.pyfile.url
        )
        self.packages = [(pack_name, self.urls, folder_name)]

    def decrypt_links(self, url):
        linklist = []
        name = self.package.name
        folder = self.package.folder

        html = self.load(url)
        titledata = re.search(self.PATTERN_TITLE, html, re.I)
        if not titledata:
            self.log_warning("No title data found, has site changed?")
        else:
            title = titledata.group("TITLE").strip()
            if title:
                name = folder = title
                self.log_debug(
                    "Package info found, name [{}] and folder [{}]".format(
                        name, folder
                    )
                )

        links = re.findall(self.PATTERN_REDIRECT_LINKS, html, re.I)
        if not links:
            self.log_error(self._("Broken for link: {}").format(link))
        else:
            for link in links:
                link = link.replace(
                    "http://sexuria.net/", "http://www.sexuria.net/"
                )
                finallink = self.load(link, just_header=True)["url"]
                if not finallink or "sexuria.net/" in finallink:
                    self.log_error(self._("Broken for link: {}").format(link))
                else:
                    linklist.append(finallink)

        #: Log result
        if not linklist:
            self.fail(self._("Unable to extract links (maybe plugin out of date?)"))
        else:
            for i, link in enumerate(linklist):
                self.log_debug(
                    "Supported link {}/{}: {}".format(i + 1, len(linklist), link)
                )

        #: All done, return to caller
        return name, linklist, folder
