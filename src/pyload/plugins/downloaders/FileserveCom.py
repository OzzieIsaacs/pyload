# -*- coding: utf-8 -*-

from ..base.xfs_downloader import XFSDownloader


class FileserveCom(XFSDownloader):
    __name__ = "FileserveCom"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?fileserve\.com/(?P<ID>[A-Za-z0-9]+)(?:/[^/]+)?"

    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Fileserve.com downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("ChatGPT", "")]

    PLUGIN_DOMAIN = "fileserve.com"

    URL_REPLACEMENTS = [
        (__pattern__ + ".*", r"https://fileserve.com/\g<ID>")
    ]

    NAME_PATTERN = r'class="filename-text">\s*(?P<N>[^<]+)|name="fname"\s+value="(?P<N2>[^"]+)"'

    SIZE_PATTERN = r'class="file-size">\s*(?P<S>[\d.,]+)\s*(?P<U>[KMGTP]?B)|File Size:\s*</[^>]+>\s*(?P<S2>[\d.,]+)\s*(?P<U2>[KMGTP]?B)'

    OFFLINE_PATTERN = r'File Not Found|File Deleted|File was removed|No such file'

    WAIT_PATTERN = r'id="countdown"[^>]*value=".*?(\d+).*?"|<span id="countdown_str".*?>(\d+)</span>'

    DL_LIMIT_PATTERN = r'You have reached your download limit|download limit'

    HCAPTCHA_PATTERN = r'class="h-captcha".*?data-sitekey="([^"]+)"'

    LINK_PATTERN = r'<a[^>]+id="direct_download_btn"[^>]+href="([^"]+)"'