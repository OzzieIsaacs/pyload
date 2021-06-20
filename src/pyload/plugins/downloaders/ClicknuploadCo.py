# -*- coding: utf-8 -*-

from ..base.xfs_downloader import XFSDownloader


class ClicknuploadCo(XFSDownloader):
    __name__ = "ClicknuploadCo"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://clicknupload.co/\w{12}"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Clicknupload.co hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "clicknupload.co"

    NAME_PATTERN = r"<h2 style=\"word-break: break-all;\">Datei herunterladen (?P<N>.+?)</h2>"
    SIZE_PATTERN = r"</font> \((?P<S>[\d.,]+) (?P<U>[\w^_]+)\)</font>"

    LINK_PATTERN = r"class=\"downloadbtn\" href=\"javascript:void\(0\);\" onClick=\"window.open\('(.+?)'\);"
    WAIT_PATTERN = r'<span id="countdown"><br>Wait<br /><span class="seconds">(\d+)</span> <br />Seconds<br /></span>'