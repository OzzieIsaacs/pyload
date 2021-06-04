# -*- coding: utf-8 -*-

import re
import urllib.parse

from ..base.simple_decrypter import SimpleDecrypter
from ..anticaptchas.ReCaptcha import ReCaptcha

class DlCryptNet(SimpleDecrypter):
    __name__ = "DlCryptNet"
    __type__ = "decrypter"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?dlcrypt\.net/gets/\w+"
    __config__ = [
        ("enabled", "bool", "Activated", True),
        ("use_premium", "bool", "Use premium account if available", True),
        (
            "folder_per_package",
            "Default;Yes;No",
            "Create folder for each package",
            "Default",
        ),
        ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10),
    ]

    __description__ = """Dlcrypt.net decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    WAIT_PATTERN = r'<span id="timer">Wait <span id="progressBar">(\d+)'
    RECAPTCHA_PATTERN = r"g-recaptcha.*?sitekey=[\"']([^\"]*)"
    LINK_FREE_PATTERN = r'<a href="(.*)" target="_blank" title'

    def handle_free(self, pyfile):
        m = re.search(r'class="btn btn-primary" href="\.\./(views/\w+)"><i class="fa fa-link"', self.data)

        recaptcha = ReCaptcha(self.pyfile)
        captcha_key = recaptcha.detect_key()

        if captcha_key:
            self.captcha = recaptcha
            response, challenge = recaptcha.challenge(captcha_key)
            file = self.load("https://dlcrypt.net/{}".format(m.group(1)))
        links = re.findall(self.LINK_FREE_PATTERN, file)
        if not links:
            self.error(self._("Free decrypted link not found"))
        else:
            self.links.extend(links)

