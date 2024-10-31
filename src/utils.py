import os
import json
import csv
from collections import defaultdict


def object_reader(directory: str, key: str):
    folder = os.path.join(directory, key)
    if not os.path.exists(folder):
        return []
    for file in os.listdir(folder):
        if not file.endswith('.jsonl'):
            continue
        with open(os.path.join(folder, file), 'rt') as f:
            for row in f.readlines():
                if row:
                    yield json.loads(row)


def get_latest_extract_id(directory):
    dirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and d.isnumeric()]
    return max(dirs, key=int) if dirs else None


def get_unique_extracts(directory):
    url_mappings = defaultdict(set)
    for extract_id in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, extract_id)) or not os.path.exists(
                os.path.join(directory, extract_id, 'plan.json')):
            continue
        with open(os.path.join(directory, extract_id, 'plan.json'), 'rt') as f:
            plan = json.load(f)
            url_mappings[plan['url']].add(extract_id)
    return {k: max(v) for k, v in url_mappings.items()}


def multi_extract_object_reader(directory: str, mapping: dict[str: str], key):
    for url, extract_id in mapping.items():
        for row in object_reader(directory=os.path.join(directory, extract_id), key=key):
            yield url, row


def export_csv(directory, name, data):
    if data:
        with open(os.path.join(directory, f'{name}.csv'), 'wt') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


def export_jsonl(directory: str, name: str, data: list, idx=0):
    filename = f"{directory}/{name}/results.{idx + 1}.jsonl"
    with open(filename, 'wt') as f:
        for i in data:
            f.write(json.dumps(i['obj']) + '\n')
    return filename


def load_csv(directory, filename, coerce_booleans=True):
    if not os.path.exists(os.path.join(directory, filename)):
        return []
    with open(os.path.join(directory, filename), 'rt') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        if coerce_booleans:
            for row in data:
                for k, v in row.items():
                    if v.lower() in ['true', 'false']:
                        row[k] = v.lower() == 'true'
        return data
