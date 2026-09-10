#!/usr/bin/env python3
"""
Sync version from pyproject.toml to config.py
This script is called by GitHub Actions after semantic-release updates the version.

semantic-release owns the base semver in pyproject.toml; this fork appends the
PEP 440 local segment "+fvoges" to config.__version__ so the running server and
the `version` tool clearly report a downstream build.
"""

import re
from datetime import datetime

import toml

# PEP 440 local version identifier appended to the base semver for this fork.
FORK_LOCAL_SEGMENT = "fvoges"


def update_config_version():
    # Read version from pyproject.toml
    with open("pyproject.toml") as f:
        data = toml.load(f)
        version = data["project"]["version"]

    # Tag it as a fork build (idempotent - don't double-append on reruns)
    base_version = version.split("+", 1)[0]
    fork_version = f"{base_version}+{FORK_LOCAL_SEGMENT}"

    # Read current config.py
    with open("config.py") as f:
        content = f.read()

    # Update version
    content = re.sub(r'__version__ = "[^"]*"', f'__version__ = "{fork_version}"', content)

    # Update date to current date
    today = datetime.now().strftime("%Y-%m-%d")
    content = re.sub(r'__updated__ = "[^"]*"', f'__updated__ = "{today}"', content)

    # Write back
    with open("config.py", "w") as f:
        f.write(content)

    print(f"Updated config.py to version {fork_version}")


if __name__ == "__main__":
    update_config_version()
