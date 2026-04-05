import traceback
from ast import literal_eval
from itertools import chain
from logging import getLogger
from typing import Any
from urllib.parse import unquote

import flask
from flask.json import jsonify

from pyload import APPID

from ..api_docs.openapi_specification_generator import OpenAPISpecificationGenerator
from ..cw_login import current_user, login_user
from ..helpers import apikey_auth, csrf_exempt, is_authenticated, render_template

bp = flask.Blueprint("api", __name__)
log = getLogger(APPID)


# accepting positional arguments, as well as kwargs via post and get
@bp.route("/api/<func>", methods=["GET", "POST"], endpoint="rpc")
@bp.route("/api/<func>/<args>", methods=["GET", "POST"], endpoint="rpc")
# @apiver_check
@apikey_auth
def rpc(func, args=""):
    if func.startswith("_"):
        flask.flash(f"Invalid API call '{func}'")
        return jsonify({'error': "Forbidden"}), 403

    api = flask.current_app.config["PYLOAD_API"]

    # Enforce HTTP method for the API method
    expected = api._required_http_method_for_api(func)
    if expected is None:
        return jsonify({'error': "Not Found"}), 404

    actual = flask.request.method
    if actual != expected:
        err_message = f"Method not allowed in API {func}(): Expected {expected}, got {actual}"
        log.error(err_message)
        return jsonify({'error': err_message}), 405

    if not current_user.is_authenticated:
        user = flask.request.authorization.get("username", "")
        password = flask.request.authorization.get("password", "")

        sanitized_user = user.replace("\n", "\\n").replace("\r", "\\r")
        if user:
            user_info = api.check_auth(user, password)
            if user_info:
                s = login_user(user_info)
            else:
                log.error(f"API access failed for user '{sanitized_user}'")
                return jsonify({'error': "Login required"}), 401

    # Check permissions
    if not api.is_authorized(func, {"role": current_user.role, "permission": current_user.permission}):
        log.error(f"API access denied for function '{func}'")
        return jsonify({'error': "Access denied"}), 401

    # get path parameters
    args = args.split(",")
    if len(args) == 1 and not args[0]:
        args = []

    # get query parameters
    kwargs = {}
    for x, y in chain(flask.request.args.items(), flask.request.form.items()):
        kwargs[x] = unquote(y)

    try:
        if flask.request.mimetype == "application/json":
            # get JSON request body
            json_request_body = flask.request.get_json()
            response = jsonify(getattr(api, func)(**json_request_body))
        elif flask.request.mimetype == "multipart/form-data":
            # get uploaded file - currently only single file upload possible
            name, file = next(iter(flask.request.files.items()))
            response = jsonify(getattr(api, func)(
                **{x: _parse_parameter(y) for x, y in kwargs.items()},
                **{name: file.read()}
            ))
        else:
            response = jsonify(getattr(api, func)(
                *[_parse_parameter(x) for x in args],
                **{x: _parse_parameter(y) for x, y in kwargs.items()},
            ))
    except Exception as exc:
        api.pyload.log.error(f"API error in '{func}'",
            exc_info=api.pyload.debug > 1,
            stack_info=api.pyload.debug > 2
        )

        response = jsonify({"error": "Internal server error"}), 500

    return response


def _parse_parameter(param: str) -> Any:
    if param == "true":
        return True
    elif param == "false":
        return False
    else:
        try:
            return literal_eval(param)
        except (ValueError, SyntaxError):
            # this is required to allow string parameters without extra quotes
            return literal_eval("\"" + param + "\"")


@bp.route("/api/openapi.json", methods=["GET"])
def api_docs():
    """Return OpenAPI specification JSON"""
    api = flask.current_app.config["PYLOAD_API"]

    s = flask.session
    basic_auth = flask.request.authorization

    if basic_auth:
        user_info = api.check_auth(basic_auth.username, basic_auth.password)
        if not user_info:
            return "Forbidden", 403
    elif not is_authenticated(s):
        return "Authentication required", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
    else:
        user_info = {"role": s["role"], "permission": s["perms"], "id": s["id"]}

    if user_info["role"] != 0:  #: Role.ADMIN
        return "Forbidden", 403

    openapi_spec = OpenAPISpecificationGenerator(api=api).generate_openapi_json()
    return openapi_spec


@bp.route("/api", methods=["GET"], strict_slashes=False)
def swagger_ui():
    """Serve Swagger UI with the API documentation"""
    api = flask.current_app.config["PYLOAD_API"]

    s = flask.session
    basic_auth = flask.request.authorization

    if basic_auth:
        user_info = api.check_auth(basic_auth.username, basic_auth.password)
        if not user_info:
            return "Forbidden", 403
    elif not is_authenticated(s):
        return "Authentication required", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
    else:
        user_info = {"role": s["role"], "permission": s["perms"], "id": s["id"]}

    if user_info["role"] != 0:  #: Role.ADMIN
        return "Forbidden", 403

    return flask.send_from_directory("static", "swagger.html")


@bp.route("/api/login", methods=["POST"], endpoint="login")
@csrf_exempt
# @apiver_check
def login():
    return "Obsolete API", 404


@bp.route("/api/logout", endpoint="logout")
# @apiver_check
def logout():
    return "Obsolete API", 404
