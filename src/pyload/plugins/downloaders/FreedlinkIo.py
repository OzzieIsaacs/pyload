from ..base.xfs_downloader import XFSDownloader


class FreedlinkIo(XFSDownloader):
    __name__ = "FreedlinkIo"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    # https://frdl.io/ikjwwtuq0re0
    __pattern__ = r"https?://(?:www\.)?(?:frdl\.(?:io|my)|freedl\.ink)/(?P<ID>\w{12})(?:/\S*)?"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Freedlink.io downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "freedl.ink"

    URL_REPLACEMENTS = [
        (__pattern__ + ".*", r"https://frdl.my/\g<ID>"),
    ]

    #: Name and size shown on download page
    NAME_PATTERN = r'<div class="maxtxt">\s*(?P<N>[^<]+)\s*</div>'
    SIZE_PATTERN = r'<span class="badge[^"]*">\s*(?P<S>[\d.,]+)\s*(?P<U>[\w^_]+)\s*</span>'

    #: Shown when file is gone
    OFFLINE_PATTERN = r">File Not Found|>The file you are trying|has been removed"
    DL_LIMIT_PATTERN = r"You have to wait (.+?) till next download"

    #: Wait countdown can be either in HTML or JS initialization
    WAIT_PATTERN = (
        r'class="seconds">\s*(\d+)\s*<'
        r'|id="seconds">\s*(\d+)\s*<'
        r'|var\s+sec\s*=\s*(\d+)'
    )

    #: hCaptcha is used on the free form
    HCAPTCHA_PATTERN = r'class="h-captcha"[^>]*data-sitekey="([^"]+)"'

    #: Prefer the FREE1 form where download_free is present
    FORM_PATTERN = r'name="FREE1"'

    PREMIUM_ONLY_PATTERN = r">This file is available for Premium Users only"
    ERROR_PATTERN = (
        r'(?:class=["\']err["\'].*?>|<[Cc]enter><b>|>Error</td>|>\(ERROR:)'
        r'(?:\s*<.+?>\s*)*(.+?)(?:["\']|<|\))'
    )

    #: Fallback in case direct link appears in HTML instead of redirect header.
    #: Match by surrounding elements, not by link-provider domain.
    LINK_PATTERN = (
        r'<p[^>]*class="done"[^>]*>.*?</p>\s*'
        r'<a[^>]*href="(https?://[^"]+)"[^>]*>\s*Download Now\s*</a>'
    )

    def _post_parameters(self):
        inputs = super()._post_parameters()
        if not self.premium:
            inputs["download_free"] = "1"
        return inputs
