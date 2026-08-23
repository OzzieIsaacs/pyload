from ..base.xfs_downloader import XFSDownloader


class Mega4uploadNet(XFSDownloader):
    __name__ = "Mega4uploadNet"
    __type__ = "downloader"
    __version__ = "0.01"
    __status__ = "testing"

    # https://mega4upload.net/0ldpjaetvxc8
    __pattern__ = r"https?://(?:www\.)?mega4upload\.net/(?P<ID>\w{12})(?:/\S*)?"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Mega4upload.net downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "mega4upload.net"

    URL_REPLACEMENTS = [
        (__pattern__ + ".*", r"https://mega4upload.net/\g<ID>"),
    ]

    NAME_PATTERN = (
        r'(?:<h1 class="dl-hero__title">|<span id="file-name">)\s*'
        r'(?P<N>[^<]+)\s*(?:</h1>|</span>)'
    )
    SIZE_PATTERN = (
        r'(?:<small>\s*size:\s*|<span class="dl-meta__chip">.*?>)\s*'
        r'(?P<S>[\d.,]+)\s*(?P<U>[\w^_]+)\s*(?:</small>|</span>)'
    )

    OFFLINE_PATTERN = r">File Not Found|>The file you are trying|has been removed"
    DL_LIMIT_PATTERN = r"You have to wait (.+?) till next download"

    WAIT_PATTERN = (
        r'<span id="seconds">\s*(\d+)\s*</span>'
        r'|<span id="countdown_str".*?>(\d+)</span>'
        r'|id="countdown"\s+value=".*?(\d+).*?"'
    )
    TURNSTILE_PATTERN = r'class="cf-turnstile"[^>]*data-sitekey="([^"]+)"'

    PREMIUM_ONLY_PATTERN = r">This file is available for Premium Users only"
    ERROR_PATTERN = (
        r'(?:class=["\']err["\'].*?>|<[Cc]enter><b>|>Error</td>|>\(ERROR:)'
        r'(?:\s*<.+?>\s*)*(.+?)(?:["\']|<|\))'
    )

    LINK_PATTERN = (
        r'<input[^>]*id="dl2link"[^>]*value="'
        r'(https?://[^"\'>\s]+(?:/d/|/files?/)[^"\'>\s]+)"'
    )

    def _post_parameters(self):
        inputs = super()._post_parameters()

        if not self.premium:
            rand = inputs.get("rand")
            if rand:
                # JS equivalent:
                # s = "m4u:" + rand
                # h = 0; h = (h * 131 + ord(ch)) % 2000003
                h = 0
                for ch in "m4u:" + rand:
                    h = (h * 131 + ord(ch)) % 2000003
                inputs["human_proof"] = str(h)

            if "adblock_detected" in inputs and not inputs["adblock_detected"]:
                inputs["adblock_detected"] = "0"

        return inputs
