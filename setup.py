#!/usr/bin/env python
#       ____________
#   ___/       |    \_____________ _                 _ ___
#  /        ___/    |    _ __ _  _| |   ___  __ _ __| |   \
# /    \___/  ______/   | '_ \ || | |__/ _ \/ _` / _` |    \
# \            ◯ |      | .__/\_, |____\___/\__,_\__,_|    /
#  \_______\    /_______|_|   |__/________________________/
#           \  /
#            \/

import os

# from pkg_resources import VersionConflict, require
from setuptools import setup

# import sys


# try:
#     require("setuptools>=38.3")
# except VersionConflict:
#     print("Error: version of setuptools is too old (<38.3)!")
#     sys.exit(1)


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
            ]
        },
    )
