import json

from ..base.simple_decrypter import SimpleDecrypter


class NitroflareComFolder(SimpleDecrypter):
    __name__ = "NitroflareComFolder"
    __type__ = "decrypter"
    __version__ = "0.08"
    __status__ = "testing"

    __pattern__ = r"https?://(?:www\.)?nitroflare\.com/folder/(?P<USER>\d+)/(?P<ID>[\w=]+)"
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

    __description__ = """Nitroflare.com folder decrypter plugin"""
    __license__ = "GPLv3"
    __authors__ = [("Walter Purcaro", "vuolter@gmail.com")]

    def get_links(self):
        i = 1
        links = list()
        while i: 
            html = self.load("http://nitroflare.com/ajax/folder.php",
                             post={"userId": self.info["pattern"]["USER"],
                                   "folder": self.info["pattern"]["ID"],
                                   "page": i,
                                   "perPage": 100,
                                   },
                             )
            res = json.loads(html)
            if "files" in res:
                links.extend([link["url"] for link in res["files"]])
            if res["total"] > i*100:
                i += 1
            else:
                break
        if res["name"]:
             self.pyfile.name = res["name"]
        else:
             self.offline()
        return links if links else None
