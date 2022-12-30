# -*- coding: utf-8 -*-

import json
import re

from pyload.core.network.http.exceptions import BadHeader

from ..base.simple_decrypter import SimpleDecrypter


class Keep2ShareCcFolder(SimpleDecrypter):
    __name__ = "Keep2ShareCcFolder"
    __type__ = "decrypter"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?(keep2share|k2s|keep2s)\.cc/folder/(?P<ID>\w+)"
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

    __description__ = """Keep2Share.cc folder decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [
        ("stickell", "l.stickell@yahoo.it"),
        ("Walter Purcaro", "vuolter@gmail.com"),
        ("GammaC0de", "nitzo2001[AT]yahoo[DOT]com"),
        ("OzzieIsaacs", "Ozzie.Fernandez.Isaacs@googlemail.com")
    ]

    URL_REPLACEMENTS = [(__pattern__ + ".*", r"https://k2s.cc/folder/\g<ID>")]

    API_URL = "https://keep2share.cc/api/v2/"
    #: See https://keep2share.github.io/api/ https://github.com/keep2share/api

    def api_request(self, method, **kwargs):
        html = self.load(self.API_URL + method, post=json.dumps(kwargs))
        return json.loads(html)

    def setup(self):
        self.multi_dl = self.premium
        self.resume_download = True

    def handle_free(self, pyfile):
        file_id = self.info["pattern"]["ID"]
        files_in_folder = self.api_request("getFileStatus", id=[file_id], extended_info=False)
        for folder_file in files_in_folder['files']:
            self.links.extend(["https://k2s.cc/file/"+ folder_file['id']])
