# -*- coding: utf-8 -*-

from ..base.xfs_downloader import XFSDownloader


class FastfileCc(XFSDownloader):
    __name__ = "FastfileCc"
    __type__ = "downloader"
    __version__ = "0.14"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?(fastfile\.cc)/\w{12}"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Fastfile.cc downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "fastfile.cc"

    OFFLINE_PATTERN = r">&quot;File Not Found|File has been removed"

    # LINK_PATTERN = r'<span class="btext">Downfghgfdhload</span>'

    SIZE_PATTERN = r'</b> \(((?P<S>[\d.,]+) (?P<U>[\w^_]+)\)</h2>)'
    NAME_PATTERN = r'<h2>Download File<br><b>(?P<N>.+?)</b>'
    WAIT_PATTERN = '<span id="countdown"><br>Wait <span class="seconds">(\d+)</span> seconds<br'