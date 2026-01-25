# -*- coding: utf-8 -*-

from ..base.simple_decrypter import SimpleDecrypter


class RapidcloudCcFolder(SimpleDecrypter):
    __name__ = "RapidcloudCcFolder"
    __type__ = "decrypter"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://rapidcloud\.cc/(?P<ID>\w{10}(/|$))"
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

    __description__ = """Rapidcloud.cc folder decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    LINK_PATTERN = r'<a href="(https:\/\/rapidcloud.cc\/\w{12})\/.*target="_blank"><b>'
    NAME_PATTERN = r'<h2>(.*)</h2>'
