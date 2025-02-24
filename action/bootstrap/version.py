import os
import json
from platform import machine
from typing import cast

VAR_NAME = "CXX_FLOW_VERSION"
VARIABLE = ""

try:
    with open(".flow/flow.py", encoding="UTF-8") as flow_py:
        for line in flow_py:
            if not line.startswith(VAR_NAME):
                continue

            var_list = line.split("=", 1)
            if len(var_list) != 2:
                continue

            var = var_list[0].strip()
            if var != VAR_NAME:
                continue

            val = var_list[1].strip()
            start = val[:1]
            if start not in "\"'":
                continue

            VARIABLE = val[1:].split(start, 1)[0].strip()
            break
except FileNotFoundError:
    pass

runner = cast(dict, json.loads(os.environ["RUNNER_CONTEXT"]))
runner_os = runner.get("os", os.name)
runner_arch = runner.get("arch", machine() or "unk-arch")

pip_cache_key = f"{runner_os}-{runner_arch}-{VARIABLE}"

with open(os.environ["GITHUB_OUTPUT"], "a", encoding="UTF-8") as out:
    print(f"version={VARIABLE}", file=out)
    print(f"pip-cache-key={pip_cache_key}", file=out)

print(json.loads(os.environ["RUNNER_CONTEXT"]))
