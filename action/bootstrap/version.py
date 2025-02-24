import os
import json
from pprint import pprint

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

with open(os.environ["GITHUB_OUTPUT"], "a", encoding="UTF-8") as out:
    print(f"value={VARIABLE}", file=out)

pprint(json.loads(os.environ["GITHUB_CONTEXT"]))
