from datetime import datetime
import os
import json


def generate_hash_id(data):
    """Generate a consistent uuid for a given input

    :return: a UUID4 formatted string
    """
    import json
    import uuid
    import hashlib
    hash_id = uuid.UUID(
        hashlib.md5(
            str(json.dumps(data, sort_keys=True)).encode('utf-8')
        ).hexdigest()
    )
    return str(hash_id)


def convert_to_timestamp(value, **kwargs):
    if isinstance(value, str):
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z').timestamp()
    elif isinstance(value, int):
        return value / 1000
    else:
        return value


def extract_path_value(path, js):
    keys = path.split('.')
    if keys[0] == '$':
        keys = keys[1:]
    if len(keys) > 1:
        return extract_path_value('.'.join(keys[1:]), js.get(keys[0], dict()))
    else:
        return js.get(keys[0])


def process_entity(extract_directory, entity_type, key='key'):
    entities = list()
    for entity in entity_reader(extract_directory=extract_directory, entity_type=entity_type):
        entities.append(extract_path_value(path=key, js=entity))
    return entities


def entity_reader(extract_directory, entity_type):
    folder = os.path.join(extract_directory, f"./{entity_type}/")
    if not os.path.exists(folder):
        return []
    for file in os.listdir(folder):
        if not file.endswith('.jsonl'):
            continue
        with open(os.path.join(folder, file), 'rt') as f:
            for row in f.readlines():
                if row:
                    yield json.loads(row)
