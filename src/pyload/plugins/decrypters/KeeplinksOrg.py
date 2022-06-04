# -*- coding: utf-8 -*-
import re

from ..anticaptchas.ReCaptcha import ReCaptcha
from ..base.decrypter import BaseDecrypter


class KeeplinksOrg(BaseDecrypter):
    __name__ = "KeeplinksOrg"
    __type__ = "decrypter"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?keeplinks\.org/p77/\w+"
    # __pattern__ = r"https?://(?:www\.)?keeplinks\.org/p77/.*"
    __config__ = [
        ("enabled", "bool", "Activated", True),
    ]

    __description__ = """Keeplinks.org decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    def decrypt(self, pyfile):
        inputs={}
        html = self.load(
            self.pyfile.url, post={"showpageval": "1"}
        )
        recaptcha = ReCaptcha(self.pyfile)
        recaptcha_key = recaptcha.detect_key()
        if recaptcha_key:
            self.captcha = recaptcha
            response = self.captcha.challenge(recaptcha_key)
            inputs["g-recaptcha-response"] = response
        m = re.search(r'id="hiddenaction"\svalue="(.+?)"/>', html, re.MULTILINE)
        inputs["captchatype"] = "Re"
        inputs["myhiddenpwd"] = ""
        inputs["hiddencaptcha"] = "1"
        if m is not None:
            inputs["hiddenaction"] = m.group(1)
        self.data = self.load(self.pyfile.url, post=inputs)
        m = re.findall(r'<a href="(.+?)\starget="_blank"\sclass="selecttext\slive"', self.data)
        if m is not None:
            self.packages = [
                (pyfile.package().name, m, pyfile.package().name)
            ]
