#!/usr/bin/env python
#       ____________
#   ___/       |    \_____________ _                 _ ___
#  /        ___/    |    _ __ _  _| |   ___  __ _ __| |   \
# /    \___/  ______/   | '_ \ || | |__/ _ \/ _` / _` |    \
# \            ◯ |      | .__/\_, |____\___/\__,_\__,_|    /
#  \_______\    /_______|_|   |__/________________________/
#           \  /
#            \/

import ast
import os
from setuptools import setup


def extract_default_cfg(fileobj, keywords, comment_tags, options):
    """Extract translatable labels from core/config/default.cfg."""
    for lineno, line in enumerate(fileobj, start=1):
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if " - " in stripped:
            _, title = stripped.split(" - ", 1)
            title = title.strip()
            if title.endswith(":"):
                title = title[:-1].rstrip()
            if len(title) >= 2 and title[0] == '"' and title[-1] == '"':
                message = title[1:-1].strip()
                if message:
                    yield lineno, "_", message, []
                continue

        quote_parts = line.split('"')
        if len(quote_parts) >= 3:
            message = quote_parts[1].strip()
            if message:
                yield lineno, "_", message, []
        elif line[:1].isspace():
            if ":" in line:
                _, after_colon = line.split(":", 1)
                message = after_colon.split("=", 1)[0].strip()
                if message:
                    yield lineno, "_", message, []


def _to_text(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            elif isinstance(v, ast.Str):
                parts.append(v.s)
            else:
                return None
        return "".join(parts)
    return None


def extract_plugin_config(fileobj, keywords, comment_tags, options):
    """Extract plugin __config__ labels (3rd tuple item) from Python files."""
    source = fileobj.read()
    if isinstance(source, bytes):
        source = source.decode("utf-8", errors="replace")

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue

            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            if "__config__" not in targets:
                continue

            if not isinstance(stmt.value, (ast.List, ast.Tuple)):
                continue

            for item in stmt.value.elts:
                if not isinstance(item, (ast.List, ast.Tuple)) or len(item.elts) < 3:
                    continue
                message = _to_text(item.elts[2])
                if message:
                    yield getattr(item, "lineno", getattr(stmt, "lineno", 1)), "_", message, []


def retrieve_version():
    version = None
    build = (
        int(os.environ["PYLOAD_BUILD"].strip()) if "PYLOAD_BUILD" in os.environ else 0
    )

    filename = os.path.join(os.path.dirname(__file__), "VERSION")
    with open(filename) as fp:
        version = os.environ.get("PYLOAD_VERSION", fp.read()).strip()

    return f"{version}.dev{build}" if build else version


# TODO: BuildDocs running `sphinx-apidoc`
if __name__ == "__main__":
    setup(
        version=retrieve_version(),
        entry_points={
            "babel.extractors": [
                "defaultcfg = setup:extract_default_cfg",
                "pluginconfig = setup:extract_plugin_config",
            ]
        },
    )
