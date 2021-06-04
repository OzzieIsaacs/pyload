# -*- coding: utf-8 -*-

from ..base.simple_decrypter import SimpleDecrypter


class RapidgatorNetFolder(SimpleDecrypter):
    __name__ = "RapidgatorNetFolder"
    __type__ = "decrypter"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?(rapidgator\.net)/folder/\d{7}/\w+\.html"
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

    __description__ = """Rapidgator.net folder decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")]

    LINK_FREE_PATTERN = r'<td><a href="(/file/\w+)/.*"><img src='
    NAME_PATTERN = r'class="table_header">\s+(?P<N>.+?)</div>'


