import json, pathlib


with open(pathlib.Path(__file__).parent / "permissions.json") as f:
    roles_access_scope = json.load(f)


def get_scopes(role: str) -> str:
    roles = role.split(" ")
    res = ""
    for rl in roles:
        for scope in roles_access_scope.get(rl, ""):
            res = res + scope + " "
    return res