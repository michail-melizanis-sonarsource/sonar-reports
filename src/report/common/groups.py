from parser import extract_path_value
from utils import multi_extract_object_reader

def process_groups(directory, extract_mapping, server_id_mapping):
    groups = list()
    for url, group in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getGroups'):
        server_id = server_id_mapping[url]
        groups.append(
            dict(
            server_id=server_id,
            name=extract_path_value(obj=group, path='$.name'),
            permissions=extract_path_value(obj=group, path='$.permissions'),
            is_managed=extract_path_value(obj=group, path='$.managed')
        ))
    return groups