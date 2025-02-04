from collections import defaultdict

from report.common.groups import process_groups
from report.utils import generate_section
from utils import multi_extract_object_reader
from parser import extract_path_value
from datetime import datetime, timedelta, UTC


def process_user(directory, extract_mapping, server_id_mapping):
    server_users = defaultdict(list)
    for url, user in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getUsers'):
        server_id = server_id_mapping[url]
        server_users[server_id].append(user)
    return server_users


def generate_user_markdown(directory, extract_mapping, server_id_mapping):
    users = process_user(directory=directory, extract_mapping=extract_mapping,
                                server_id_mapping=server_id_mapping)
    groups = process_groups(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    row = dict(
        total=sum([len(i) for i in users.values()]),
        unique=len(
            set([i['externalIdentity'] if i.get('externalIdentity') else i['login'] for i in sum(users.values(), []) if i.get('login')])),
        active=len([i for i in sum(users.values(), []) if
                    i.get('lastConnectionDate') and datetime.strptime(i['lastConnectionDate'],
                                                                      '%Y-%m-%dT%H:%M:%S%z') > datetime.now(tz=UTC) - timedelta(
                        days=30)]),
        sso=len([i for i in sum(users.values(), []) if i.get('externalProvider')]),
        groups=len(set([i['name'] for i in groups]))
    )
    md = generate_section(
        headers_mapping={
            "Total Users": "total",
            "Unique Users": "unique",
            "Active Users": "active",
            "SSO Users": "sso",
            "Groups": "groups"
        },
        rows=[
            row
        ],
        title="User Management",
        level=3
    )
    return md, users, groups
