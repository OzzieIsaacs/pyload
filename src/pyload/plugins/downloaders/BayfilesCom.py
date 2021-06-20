# -*- coding: utf-8 -*-

from ..base.simple_downloader import SimpleDownloader


class BayfilesCom(SimpleDownloader):
    __name__ = "BayfilesCom"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?bayfiles?\.com/(?P<ID>\w+)"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Bayfiles.com downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    NAME_PATTERN = r'<h1 class="text-center text-wordwrap">(?P<N>.+?)</h1>'
    SIZE_PATTERN = r"\((?P<S>[\d.,]+) (?P<U>[\w^_]+)\)</a>"

    LINK_PATTERN = r'href="(https://cdn-\d+.bayfiles.com/.+?)"'

    def setup(self):
        self.multi_dl = True
        self.resume_download = True
        self.chunk_limit = -1

