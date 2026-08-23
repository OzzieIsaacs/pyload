from ..base.xfs_downloader import XFSDownloader


class FilespayoutsCom(XFSDownloader):
    __name__ = "FilespayoutsCom"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    # https://filespayouts.com/mo4kwaqy0s9d/mutzenrachbell71.rar
    __pattern__ = r"https?://(?:www\.)?filespayouts\.com/\w{12}/(?P<id>)"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Filespayouts.Com downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "filespayouts.com"

    #: Filename and size shown on the download page
    NAME_PATTERN = r'<h1 class="download-title[^"]*">\s*(?P<N>.+?)\s*</h1>'
    SIZE_PATTERN = r'<span[^>]*>\s*(?P<S>[\d.,]+)\s*(?P<U>[\w^_]+)\s*</span>'

    #: Shown when the file has been deleted
    OFFLINE_PATTERN = r">File Not Found|>The file you are trying|has been removed"

    #: Countdown on the free-download waiting page (XFS standard)
    WAIT_PATTERN = r'<span id="countdown_str".*?>(\d+)</span>|id="countdown"\s+value=".*?(\d+).*?"'

    #: The direct download link is delivered via HTTP redirect after the
    #: second POST (op=download2).  XFSDownloader catches the Location header
    #: automatically; the pattern below is a fallback for pages that embed it.
    LINK_PATTERN = r'(https?://(?:www\.)?(?:[^\s"\'<>]*?filespayouts\.com|\d{1,3}(?:\.\d{1,3}){3})(?::\d+)?(?:/d/|(?:/files)?/\d+/\w+/).+?)["\' <]'

    PREMIUM_ONLY_PATTERN = r">This file is available for Premium Users only"
    ERROR_PATTERN = (
        r'(?:class=["\']err["\'].*?>|<[Cc]enter><b>|>Error</td>|>\(ERROR:)'
        r'(?:\s*<.+?>\s*)*(.+?)(?:["\']|<|\))'
    )
