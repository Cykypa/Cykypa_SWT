import json


def removing_duplicated(ilt):  # 列表去重
    lst = ilt
    res = []
    [res.append(c) for c in lst if c not in res]
    return res


with open('./config/new_link.json', 'r') as f:
    fails = json.load(f)
print(len(fails))
print(len(removing_duplicated(fails)))
