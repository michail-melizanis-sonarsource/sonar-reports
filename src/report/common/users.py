from utils import multi_extract_object_reader
from parser import extract_path_value

def process_user_totals(directory, extract_mapping, server_id_mapping):
    server_users = dict()
    for url, user in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getUsers'):
        server_id = server_id_mapping[url]
        server_users[server_id] = extract_path_value(obj=user, path='$.paging.total')
    return server_users