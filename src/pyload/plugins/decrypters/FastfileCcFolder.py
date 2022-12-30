# -*- coding: utf-8 -*-

from ..base.simple_decrypter import SimpleDecrypter


class FastfileCcFolder(SimpleDecrypter):
    __name__ = "FastfileCcFolder"
    __type__ = "decrypter"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?(fastfile\.cc)/users/\w+"
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

    __description__ = """Fastfile.cc folder decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    LINK_PATTERN = r'<div class="lft sec">\s+<a href="(https:\/\/fastfile.cc\/\w{12})'
    # NAME_PATTERN = r'style="color:#118bb6"><b>(?P<N>.+?)</b></a>'
