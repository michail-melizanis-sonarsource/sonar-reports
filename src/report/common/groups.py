from utils import multi_extract_object_reader

def process_groups(directory, extract_mapping, server_id_mapping):
    groups = list()
    for url, group in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getGroups'):
        server_id = server_id_mapping[url]
        groups.append(dict(
            server_id=server_id,
            name=group['name'],
            permissions=group['permissions'],
            is_managed=group.get('managed')
        ))
    return groups