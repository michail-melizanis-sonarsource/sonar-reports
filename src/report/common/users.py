from collections import defaultdict

from report.common.groups import process_groups
from report.utils import generate_section
from utils import multi_extract_object_reader
from parser import extract_path_value
from datetime import datetime, timedelta, UTC

def process_user(raw_user):
    now = datetime.now(tz=UTC)
    recent = now - timedelta(days=30)
    user = dict(
        login=extract_path_value(obj=raw_user, path='$.login'),
        external_id=extract_path_value(obj=raw_user, path='$.externalIdentity'),
        last_connection=extract_path_value(obj=raw_user, path='$.lastConnectionDate'),
        external_provider=extract_path_value(obj=raw_user, path='$.externalProvider'),
        sonar_lint_connection=extract_path_value(obj=raw_user, path='$.sonarLintLastConnectionDate'),
        is_active = False,
        is_active_sonar_lint=False
    )
    if user['last_connection']:
        user['last_connection'] = datetime.strptime(user['last_connection'], '%Y-%m-%dT%H:%M:%S%z')
        if user['last_connection'] > recent:
            user['is_active'] = True
    if user['sonar_lint_connection']:
        user['sonar_lint_connection'] = datetime.strptime(user['sonar_lint_connection'], '%Y-%m-%dT%H:%M:%S%z')
        if user['sonar_lint_connection'] > recent:
            user['is_active_sonar_lint'] = True
    return user

def process_users(directory, extract_mapping, server_id_mapping):
    server_users = defaultdict(list)
    for url, user in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getUsers'):
        server_id = server_id_mapping[url]
        server_users[server_id].append(
            process_user(raw_user=user)
        )
    return server_users


def generate_user_markdown(directory, extract_mapping, server_id_mapping):
    users = process_users(directory=directory, extract_mapping=extract_mapping,
                                server_id_mapping=server_id_mapping)
    groups = process_groups(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)

    row = dict(
        total=sum([len(i) for i in users.values()]),
        unique=len(
            set([i['external_id'] if i['external_id'] else i['login'] for i in sum(users.values(), []) if i['login']])),
        active=len([i for i in sum(users.values(), []) if i['is_active']]),
        sso=len([i for i in sum(users.values(), []) if i.get('external_provider')]),
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
