# -*- coding: utf-8 -*-

from flask_babel import Babel
from flask_caching import Cache
from flask_themes2 import Themes as _Themes

from pyload import APPID


class Themes(_Themes):
    def init_app(self, app):
        return super().init_themes(app, app_identifier=APPID)


babel = Babel()
cache = Cache()
themes = Themes()

EXTENSIONS = [babel, cache, themes]


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    '''user = getattr(g, 'user', None)
    # user = None
    if user is not None and hasattr(user, "locale"):
        if user.nickname != 'Guest':   # if the account is the guest account bypass the config lang settings
            return user.locale

    preferred = list()
    if request.accept_languages:
        for x in request.accept_languages.values():
            try:
                preferred.append(str(LC.parse(x.replace('-', '_'))))
            except (UnknownLocaleError, ValueError) as e:
                log.debug('Could not parse locale "%s": %s', x, e)'''

    return 'de'