# Copyright (c) 2025 Marcin Zdun
# This code is licensed under MIT license (see LICENSE for details)

import json
import os

from proj_flow.base import matrix

paths = ["matrix.yml"]

official = False
if "RELEASE" in os.environ and "GITHUB_ACTIONS" in os.environ:
    if not not json.loads(os.environ["RELEASE"]):
        paths.append("official.yml")

_, keys = matrix.load_matrix(*paths)
os.environ["MATRIX_KEYS"] = json.dumps(keys)
print(f"keys={json.dumps(keys)}")

if "GITHUB_ACTIONS" in os.environ:
    GITHUB_OUTPUT = os.environ.get("GITHUB_OUTPUT")
    GITHUB_ENV = os.environ.get("GITHUB_ENV")
    if GITHUB_OUTPUT is not None:
        with open(GITHUB_OUTPUT, "a", encoding="UTF-8") as github_output:
            print(f"keys={json.dumps(keys)}", file=github_output)
    if GITHUB_ENV is not None:
        with open(GITHUB_ENV, "a", encoding="UTF-8") as github_output:
            print(f"MATRIX_KEYS={json.dumps(keys)}", file=github_output)

