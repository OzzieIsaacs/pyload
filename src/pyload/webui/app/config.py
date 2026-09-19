import os
import secrets

from pyload import PKGDIR


def get_secret_key(userdir):
    data_dir = os.path.join(userdir, "data")
    secret_key_path = os.path.join(data_dir, "webui-secret.key")
    os.makedirs(data_dir, exist_ok=True)

    try:
        fd = os.open(secret_key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        with open(secret_key_path, encoding="ascii") as secret_key_file:
            secret_key = secret_key_file.read().strip()
    else:
        secret_key = secrets.token_hex(32)
        with os.fdopen(fd, "w", encoding="ascii") as secret_key_file:
            secret_key_file.write(secret_key)

    if not secret_key:
        raise ValueError(f"WebUI secret key file is empty: {secret_key_path}")

    os.chmod(secret_key_path, 0o600)
    return secret_key


def get_default_config(develop):
    return DevelopmentConfig if develop else ProductionConfig


class BaseConfig:
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  #: 16 Megabytes
    #: Extensions
    # BCRYPT_LOG_ROUNDS = 13
    # DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_DEFAULT_TIMEOUT = 300
    # SESSION_TYPE = "filesystem"


class ProductionConfig(BaseConfig):
    ENV = "production"
    SECRET_KEY = None
    #: Extensions
    CACHE_TYPE = "simple"
    LANGUAGES = ['en', 'de']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(PKGDIR, 'locale')
    # SESSION_USE_SIGNER = True


class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    SECRET_KEY = "dev"
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = True
    #: Extensions
    # DEBUG_TB_ENABLED = True
    CACHE_NO_NULL_WARNING = True
    LANGUAGES = ['en', 'de']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(PKGDIR, 'locale')
    # LOGIN_DISABLED = True
    # SESSION_PROTECTION = None


class TestingConfig(DevelopmentConfig):
    TESTING = True
    #: Extensions
    # BCRYPT_LOG_ROUNDS = 4
