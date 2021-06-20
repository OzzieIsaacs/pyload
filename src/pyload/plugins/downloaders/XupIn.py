# -*- coding: utf-8 -*-

from ..base.xfs_downloader import XFSDownloader
from ..helpers import search_pattern
from pyload.core.utils.convert import to_str
import base64
import re

class XupIn(XFSDownloader):
    __name__ = "XupIn"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://xup.in/(?P<ID>\w+)"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """xup.in hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "xup.in"

    #NAME_PATTERN = r"<h2 style=\"word-break: break-all;\">Datei herunterladen (?P<N>.+?)</h2>"
    #SIZE_PATTERN = r"</font> \((?P<S>[\d.,]+) (?P<U>[\w^_]+)\)</font>"

    # LINK_PATTERN = rb'<link rel="canonical" href="(.+?)" />'
    LINK_PATTERN = rb'<object data="(.+?)"'
    CONTENT_PATTERN = r'var zdec = "(.+?)"'


    def handle_free(self, pyfile):
        content = re.search(self.CONTENT_PATTERN, self.data)
        if content is not None:
            data = base64.b64decode(content.group(1))
            m = search_pattern(self.LINK_PATTERN, data, flags=re.S)
            if m is not None:
                self.link = to_str(m.group(1))
