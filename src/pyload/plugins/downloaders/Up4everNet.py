from ..base.xfs_downloader import XFSDownloader


class Up4everNet(XFSDownloader):
    __name__ = "Up4everNet"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    # https://www.up-4ever.net/iiwwr1iihtnk
    __pattern__ = r"https?://(?:www\.)?up-4ever\.net/(?P<ID>\w{12})(?:/\S*)?"

    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Up-4ever.net downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "up-4ever.net"

    URL_REPLACEMENTS = [
        (__pattern__ + ".*", r"https://www.up-4ever.net/\g<ID>"),
    ]

    #: Filename shown on the download page
    NAME_PATTERN = r"<h1>\s*(?P<N>.+?)\s*</h1>"

    #: File size shown in the chip row
    SIZE_PATTERN = r'<span class="u4dl-chip">.*?ph-hard-drives.*?>\s*(?P<S>[\d.,]+)\s*(?P<U>[\w^_]+)\s*</span>'

    #: Shown when the file has been deleted
    OFFLINE_PATTERN = r">File Not Found|>The file you are trying|has been removed"

    #: Countdown: <span class="countdown">Wait <span id="seconds">30</span> seconds</span>
    WAIT_PATTERN = r'<span id="seconds">(\d+)</span>|<span id="countdown_str".*?>(\d+)</span>'

    #: Direct download link – e.g. https://s7.up4ever.download:8443/d/<token>/<filename>
    LINK_PATTERN = r'href="(https?://\w+\.up4ever\.download(?::\d+)?/d/[^"]+)"'

    PREMIUM_ONLY_PATTERN = r">This file is available for Premium Users only"
    ERROR_PATTERN = (
        r'(?:class=["\']err["\'].*?>|<[Cc]enter><b>|>Error</td>|>\(ERROR:)'
        r'(?:\s*<.+?>\s*)*(.+?)(?:["\']|<|\))'
    )
