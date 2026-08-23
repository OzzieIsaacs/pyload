from ..base.xfs_downloader import XFSDownloader


class UploadrarCom(XFSDownloader):
    __name__ = "UploadrarCom"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    # https://uploadrar.com/eviecfhvy64u
    __pattern__ = r"https?://(?:www\.)?uploadrar\.com/(?P<ID>\w{12})(?:/\S*)?"

    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Uploadrar.com downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "uploadrar.com"

    URL_REPLACEMENTS = [
        (__pattern__ + ".*", r"https://uploadrar.com/\g<ID>"),
    ]

    #: Filename and size shown on the download pages
    NAME_PATTERN = (
        r'(?:<span id="file-name">|<h1[^>]*>\s*Download File)\s*'
        r'(?P<N>[^<]+)\s*(?:</span>|</h1>)'
    )
    SIZE_PATTERN = r'(?:\(\s*|size:\s*)(?P<S>[\d.,]+)\s*(?P<U>[\w^_]+)\s*\)?'

    #: Shown when the file has been deleted
    OFFLINE_PATTERN = r">File Not Found|>The file you are trying|has been removed"

    #: Countdown on the free-download waiting page
    WAIT_PATTERN = (
        r'<span id="seconds">\s*(\d+)\s*</span>'
        r'|<span id="countdown_str".*?>(\d+)</span>'
        r'|id="countdown"\s+value=".*?(\d+).*?"'
    )

    #: Redirect/fallback direct link pattern
    LINK_PATTERN = (
        r'(https?://(?:www\.)?'
        r'(?:[^\s"\'<>]*?(?:uploadrar\.com)|\d{1,3}(?:\.\d{1,3}){3})'
        r'(?::\d+)?(?:/d/|(?:/files)?/\d+/\w+/).+?)["\' <]'
    )

    PREMIUM_ONLY_PATTERN = r">This file is available for Premium Users only"
    ERROR_PATTERN = (
        r'(?:class=["\']err["\'].*?>|<[Cc]enter><b>|>Error</td>|>\(ERROR:)'
        r'(?:\s*<.+?>\s*)*(.+?)(?:["\']|<|\))'
    )
