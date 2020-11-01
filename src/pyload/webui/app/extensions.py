# -*- coding: utf-8 -*-

from flask_caching import Cache
from flask_themes2 import Themes as _Themes

from pyload import APPID


class Themes(_Themes):
    def init_app(self, app, path_prefix=""):
        return super().init_themes(app,
                                   app_identifier=APPID,
                                   theme_url_prefix=path_prefix + "/_themes")


# babel = Babel()
cache = Cache()
themes = Themes()

EXTENSIONS = [cache]

THEMES = [themes]

# BABEL = [babel]

'''@babel.localeselector
def get_locale():
    #return app.config["PYLOAD_API"]
    #return self.pyload.config.get("general", "language")
    return'''
