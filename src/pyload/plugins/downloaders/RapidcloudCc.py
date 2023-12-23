# -*- coding: utf-8 -*-

import re
from datetime import timedelta

from pyload.core.utils import parse

from ..base.xfs_downloader import XFSDownloader
from ..anticaptchas.HCaptcha import HCaptcha
from ..helpers import search_pattern, set_cookie

class RapidcloudCc(XFSDownloader):
    __name__ = "RapidcloudCc"
    __type__ = "downloader"
    __version__ = "0.02"
    __status__ = "testing"

    __pattern__ = r"https?://rapidcloud\.cc/(?P<ID>\w+)"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Rapidcloud.cc downloader plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    PLUGIN_DOMAIN = "rapidcloud.cc"

    NAME_PATTERN = r'<h4 style="color:#5b5b5b">(?P<N>.+?)</h4>'
    SIZE_PATTERN = r'<span>Size (?P<S>[\d.,]+) (?P<U>[\w^_]+)</span>'
    WAIT_PATTERN = r'<span class="seconds">(\d+)</span> Seconds'
    ERROR_PATTERN = r'<div class="alert alert-danger">\s+<strong>Oops!</strong>(.*)\s+</div>'
    ADD_WAIT_PATTERN = r"<div class='alert alert-danger'>You have to wait (\d+) minutes, (\d+) seconds till next download<br><br>Download files instantly with <a href='https://rapidcloud.cc/premium/'>Premium-account</a></div>"

    def handle_free(self, pyfile):
        for i in range(1, 6):
            self.log_debug(f"Getting download link #{i}...")

            self.check_errors()

            m = search_pattern(self.LINK_PATTERN, self.data, flags=re.S)
            if m is not None:
                self.link = m.group(1)
                break

            self.data = self.load(
                pyfile.url,
                post=self._post_parameters(),
                ref=self.pyfile.url,
                redirect=False
                # options={"ssl_verify": 0}
            )

            if "op=" not in self.last_header.get("location", "op="):
                self.link = self.last_header.get("location")
                break

            m = search_pattern(self.ERROR_PATTERN, self.data)
            if m is not None:
                self.fail(m.group(1))

            m = search_pattern(self.LINK_PATTERN, self.data, flags=re.S)
            if m is not None:
                self.link = m.group(1)
                break
        self.req.options['ssl_verify'] = False

    def _post_parameters(self):
        n = search_pattern(self.ADD_WAIT_PATTERN, self.data)
        if n is not None:
            wait_time = timedelta(minutes=int(n.group(1).strip()), seconds=int(n.group(2).strip())).total_seconds()
            self.set_wait(wait_time)
            self.wait()

        if self.FORM_PATTERN or self.FORM_INPUTS_MAP:
            action, inputs = self.parse_html_form(
                self.FORM_PATTERN or "", self.FORM_INPUTS_MAP or {}
            )
        else:
            action, inputs = self.parse_html_form(
                input_names={"op": re.compile(r"^download")}
            )

        if not inputs:
            action, inputs = self.parse_html_form("F1")
            if not inputs:
                self.retry(
                    msg=self.info.get("error") or self._("TEXTAREA F1 not found")
                )

        self.log_debug(inputs)

        if "op" in inputs:
            m = search_pattern(self.WAIT_PATTERN, self.data)
            if m is not None:
                try:
                    waitmsg = m.group(1).strip()

                except (AttributeError, IndexError):
                    waitmsg = m.group(0).strip()

                wait_time = parse.seconds(waitmsg)
                self.set_wait(wait_time)
                if (
                    wait_time
                    < timedelta(minutes=self.config.get("max_wait", 10)).total_seconds()
                    or not self.pyload.config.get("reconnect", "enabled")
                    or not self.pyload.api.is_time_reconnect()
                ):
                    self.handle_captcha(inputs)

                self.wait()
            else:
                self.handle_captcha(inputs)

            if "referer" in inputs and len(inputs["referer"]) == 0:
                inputs["referer"] = self.pyfile.url

        else:
            inputs["referer"] = self.pyfile.url

        inputs["method_free"] = "Free Download"
        inputs.pop("method_premium", None)

        return inputs
