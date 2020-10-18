# -*- coding: utf-8 -*-
import re

from ..internal.XFSHoster import XFSHoster
from ..internal.misc import search_pattern

class UploadAc(XFSHoster):
    __name__ = "UploadAc"
    __type__ = "hoster"
    __version__ = "0.01"
    __status__ = "testing"

    __pattern__ = r'https://upload\.ac/\w{12}'
    __config__ = [("activated", "bool", "Activated", True),
                  ("use_premium", "bool", "Use premium account if available", True),
                  ("fallback", "bool", "Fallback to free download if premium fails", True),
                  ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10)]

    __description__ = """Upload.ac hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("OzzieIsaacs", "ozzie.fernandez.isaacs@gmail.com")]

    PLUGIN_DOMAIN = "upload.ac"

    NAME_PATTERN = r'<h3 class="title">(?P<N>.+?)</h3>'

    LINK_PATTERN = r' \n<a href="(.+?)" \nclass="btn btn-info btn-download btn-block"'


    def handle_free(self, pyfile):

        self.check_errors()

        m = search_pattern(self.NAME_PATTERN, self.data, flags=re.S)
        if m is None:
            pyfile.setStatus("offline")
            return

        post_params = self._post_parameters()
        post_params[u'chklsAdd'] = 'on'

        self.data = self.load(pyfile.url,
                              post=self._post_parameters(),
                              ref=self.pyfile.url,
                              redirect=False)

        m = search_pattern(self.LINK_PATTERN, self.data, flags=re.M)
        if m is not None:
            self.link = m.group(1)
            return
