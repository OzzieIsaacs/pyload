import re
from urllib.parse import urljoin

import pycurl

from ..helpers import search_pattern
from ..base.xfs_downloader import XFSDownloader


class ForafileCom(XFSDownloader):
    __name__ = "ForafileCom"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    # https://forafile.com/djcj23sh1jpf/Boote_Exclusiv_-_Nr.04_2026.pdf.html
    __pattern__ = r"https?://(?:www\.)?forafile\.com/(?P<ID>\w{12})(?:/\S*)?"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Forafile.com downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "forafile.com"

    #: Filename and size shown on the download page
    NAME_PATTERN = (
        r'<h1 class="download-title[^"]*">\s*(?P<N>[^<]+)\s*</h1>'
        r'|Download File\s*(?P<N2>[^<]+)\s*</h1>'
    )
    SIZE_PATTERN = (
        r'Filesize:\s*<strong>\s*(?P<S>[\d.,]+)\s*(?P<U>[\w^_]+)\s*</strong>'
        r'|\((?P<S2>[\d.,]+)\s*(?P<U2>[\w^_]+)\)'
    )

    OFFLINE_PATTERN = r">File Not Found|>The file you are trying|has been removed"
    DL_LIMIT_PATTERN = r"You have to wait (.+?) till next download"

    WAIT_PATTERN = (
        r'<span id="seconds">\s*(\d+)\s*</span>'
        r'|<span id="countdown_str".*?>(\d+)</span>'
        r'|id="countdown"\s+value=".*?(\d+).*?"'
    )

    PREMIUM_ONLY_PATTERN = r">This file is available for Premium Users only"
    ERROR_PATTERN = (
        r'(?:class=["\']err["\'].*?>|<[Cc]enter><b>|>Error</td>|>\(ERROR:)'
        r'(?:\s*<.+?>\s*)*(.+?)(?:["\']|<|\))'
    )

    #: Ignore ad overlay links; only treat real file-server links as direct links.
    #: If not found in HTML, XFSDownloader will POST op=download2 and use the
    #: HTTP Location header (redirect=False path in base class).
    LINK_PATTERN = r'(https?://[^"\'>\s]+/files/\d+/[^"\'>\s]+)'
    AD_LINK_PATTERN = r'<a[^>]*id="download"[^>]*href="([^"]+)"'

    def _click_ad_link(self, url):
        m = search_pattern(self.AD_LINK_PATTERN, self.data, flags=re.S)
        if m is None:
            return

        # Mimic the page JS: notify /cgi-bin/counter.cgi, then open ad URL once.
        self.load(
            urljoin(url, "/cgi-bin/counter.cgi"),
            post={"download": "true"},
            referrer=url,
            redirect=False,
            just_header=True,
        )

        ad_url = urljoin(url, m.group(1).strip())
        self.load(ad_url, referrer=url, redirect=False, just_header=True)

    def _post_header_with_retries(self, url, post_data):
        retry_count = 4
        retry_wait = 3

        had_timeout = "timeout" in self.req.options
        old_timeout = self.req.options.get("timeout")
        self.req.set_option("timeout", 5)

        try:
            for attempt in range(retry_count + 1):
                try:
                    html = self.load(
                        url,
                        post=post_data,
                        # referrer=url,
                        redirect=False,
                        just_header=False,
                    )
                    return self.last_header
                except pycurl.error as exc:
                    if exc.args and exc.args[0] == pycurl.E_OPERATION_TIMEDOUT:
                        if attempt < retry_count:
                            self.wait(retry_wait)
                            continue
                        raise
                    raise
        finally:
            if had_timeout:
                self.req.set_option("timeout", old_timeout)
            else:
                self.req.delete_option("timeout")

    def handle_free(self, pyfile):
        url = self.PLUGIN_URL or pyfile.url

        if not getattr(self, "_ad_clicked", False):
            self._click_ad_link(url)
            self._ad_clicked = True

        for i in range(1, 6):
            self.load(url)
            self.log_debug(f"Getting download link #{i}...")
            self.check_errors()

            post_data = self._post_parameters()
            post_data["adblock_detected"] = "0"
            post_data["referer"] = ""
            post_data["method_free"] = ""

            for retry in range(5):
                header = self._post_header_with_retries(url, post_data)
                location = header.get("location")

                if location and "op=" not in location:
                    self.link = location
                    break

                # Server responded but without a usable Location:
                # re-post same parameters without reloading the page.
                if retry < 4:
                    self.wait(2)
            if self.link:
                break
        else:
            self.error(self._("Too many OPs"))
