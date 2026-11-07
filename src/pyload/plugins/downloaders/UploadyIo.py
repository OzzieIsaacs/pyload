import json
import re

from ..base.xfs_downloader import XFSDownloader
from ..helpers import search_pattern


class UploadyIo(XFSDownloader):
    __name__ = "UploadyIo"
    __type__ = "downloader"
    __version__ = "0.03"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?uploady\.io/(?P<ID>[a-z0-9]{12})(?:/[^?#\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("fallback", "bool", "Fallback to free download if premium fails", True),
        ("chk_filesize", "bool", "Check file size", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Uploady.io downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", None)]

    PLUGIN_DOMAIN = "uploady.io"

    URL_REPLACEMENTS = [
        (__pattern__, r"https://uploady.io/\g<ID>"),
    ]

    NAME_PATTERN = r'<[^>]+\bid=["\']fileName["\'][^>]*>\s*(?P<N>[^<]+)'
    SIZE_PATTERN = r'<span\b[^>]*\bid=["\']fsize["\'][^>]*>\s*(?P<S>[\d.,]+)\s*(?P<U>\w+)'
    OFFLINE_PATTERN = r"(?i)>\s*File Not Found|>\s*The file you are trying|file (?:was|has been) removed|file no longer available"
    WAIT_PATTERN = r'<span\b[^>]*\bid=["\'](?:free-timer|seconds|countdown_str)["\'][^>]*>\s*(\d+)'
    DL_LIMIT_PATTERN = r'<[^>]+(?=[^>]*\bid\s*=\s*["\']secleft["\'])[^>]*\bleft\s*=\s*["\'](\d+)["\']'
    ERROR_PATTERN = (
        r'<div\b[^>]*\bclass=["\'][^"\']*\b(?:alert-danger|err)\b[^"\']*["\'][^>]*>'
        r'(?!\s*Copy function available for\b)(.*?)</div>',
        re.S,
    )
    LINK_PATTERN = r'<a\b(?=[^>]*\bid=["\']downloadbtn["\'])[^>]*\bhref=["\'](https?://[^"\']+)["\']'

    def check_errors(self, data=None):
        data = data or self.data
        if not self.premium and isinstance(data, str):
            limit = search_pattern(self.DL_LIMIT_PATTERN, data)
            if limit is not None:
                wait_time = int(limit.group(1))
                self.info["error"] = self._("Download limit exceeded")
                self.log_warning(
                    self.info["error"],
                    self._("Waiting {} seconds").format(wait_time),
                )
                self.wait(
                    wait_time,
                    reconnect=wait_time > self.config.get("max_wait", 10) * 60,
                )
                self.restart(self.info["error"])

        return super().check_errors(data)

    def _post_parameters(self):
        _, form_inputs = self.parse_html_form(
            input_names={"op": re.compile(r"^download")}
        )
        rand = None
        if (
            not self.premium
            and form_inputs
            and form_inputs.get("op") == "download1"
            and "start_countdown=1" in self.data
        ):
            # The server starts the timer and replaces the form's original nonce.
            response = self.load(
                self.pyfile.url,
                get={"start_countdown": 1},
                referrer=self.pyfile.url,
            )
            try:
                countdown = json.loads(response)
            except (ValueError, TypeError):
                self.error(self._("Invalid countdown response"))

            if not isinstance(countdown, dict):
                self.error(self._("Invalid countdown response"))
            rand = countdown.get("rand")
            if not isinstance(rand, str) or not rand.strip():
                self.error(self._("Missing countdown token"))

        inputs = super()._post_parameters()
        if rand is not None:
            inputs["rand"] = rand
        if not self.premium and form_inputs and form_inputs.get("method_free"):
            inputs["method_free"] = form_inputs["method_free"]
        return inputs
