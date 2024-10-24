import os
import json


def object_reader(directory, key):
    folder = os.path.join(directory, f"./{key}/")
    if not os.path.exists(folder):
        return []
    for file in os.listdir(folder):
        if not file.endswith('.jsonl'):
            continue
        with open(os.path.join(folder, file), 'rt') as f:
            for row in f.readlines():
                if row:
                    yield json.loads(row)
