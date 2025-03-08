# -*- coding: utf-8 -*-
#       ____________
#   ___/       |    \_____________ _                 _ ___
#  /        ___/    |    _ __ _  _| |   ___  __ _ __| |   \
# /    \___/  ______/   | '_ \ || | |__/ _ \/ _` / _` |    \
# \            ◯ |      | .__/\_, |____\___/\__,_\__,_|    /
#  \_______\    /_______|_|   |__/________________________/
#           \  /
#            \/

from functools import wraps

#from sqlalchemy.sql.expression import func
from .cw_login import login_required

import flask
from flask import request, g
from flask import session as flask_session
# from flask_httpauth import HTTPBasicAuth
from werkzeug.datastructures import Authorization
from werkzeug.security import check_password_hash
# from .cw_login import current_user
from .cw_login import user_logged_in


''''@auth.verify_password
def verify_password(username, password):
    user = ub.session.query(ub.User).filter(func.lower(ub.User.name) == username.lower()).first()
    if user:
        if user.name.lower() == "guest":
            if config.config_anonbrowse == 1:
                return user
        if config.config_login_type == constants.LOGIN_LDAP and services.ldap:
            login_result, error = services.ldap.bind_user(user.name, password)
            if login_result:
                [limiter.limiter.storage.clear(k.key) for k in limiter.current_limits]
                return user
            if error is not None:
                log.error(error)
        else:
            limiter.check()
            if check_password_hash(str(user.password), password):
                [limiter.limiter.storage.clear(k.key) for k in limiter.current_limits]
                return user
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    log.warning('OPDS Login failed for user "%s" IP-address: %s', username, ip_address)
    return None'''


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        return login_required(func)(*args, **kwargs)
    return decorated_view


'''@lm.user_loader
def load_user(user_id, random, session_key):
    api = flask.current_app.config["PYLOAD_API"]
    return api.load_user(user_id) # so gehts nicht
    user = ub.session.query(ub.User).filter(ub.User.id == int(user_id)).first()
    if session_key:
        entry = ub.session.query(ub.User_Sessions).filter(ub.User_Sessions.random == random,
                                                          ub.User_Sessions.session_key == session_key).first()
        if not entry or entry.user_id != user.id:
            return None
    elif random:
        entry = ub.session.query(ub.User_Sessions).filter(ub.User_Sessions.random == random).first()
        if not entry or entry.user_id != user.id:
            return None
    return user'''


def signal_store_user_session(object, user):
    store_user_session()


def store_user_session():
    _user = flask_session.get('_user_id', "")
    _id = flask_session.get('_id', "")
    _random = flask_session.get('_random', "")
    if flask_session.get('_user_id', ""):
        '''try:
            if not check_user_session(_user, _id, _random):
                expiry = int((datetime.now()  + timedelta(days=31)).timestamp())
                user_session = User_Sessions(_user, _id, _random, expiry)
                session.add(user_session)
                session.commit()
                log.debug("Login and store session : " + _id)
            else:
                log.debug("Found stored session: " + _id)
        except (exc.OperationalError, exc.InvalidRequestError) as e:
            session.rollback()
            log.exception(e)'''
    else:
        log.error("No user id in session")


def delete_user_session(user_id, session_key):
    try:
        log.debug("Deleted session_key: " + session_key)
        session.query(User_Sessions).filter(User_Sessions.user_id == user_id,
                                            User_Sessions.session_key == session_key).delete()
        session.commit()
    except (exc.OperationalError, exc.InvalidRequestError) as ex:
        session.rollback()
        log.exception(ex)


def check_user_session(user_id, session_key, random):
    try:
        found = session.query(User_Sessions).filter(User_Sessions.user_id==user_id,
                                                    User_Sessions.session_key==session_key,
                                                    User_Sessions.random == random,
                                                    ).one_or_none()
        if found is not None:
            new_expiry = int((datetime.now()  + timedelta(days=31)).timestamp())
            if new_expiry - found.expiry > 86400:
                found.expiry = new_expiry
                session.merge(found)
                session.commit()
        return bool(found)
    except (exc.OperationalError, exc.InvalidRequestError) as e:
        session.rollback()
        log.exception(e)
        return False


user_logged_in.connect(signal_store_user_session)
