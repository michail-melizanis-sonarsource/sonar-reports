from collections import defaultdict

from parser import extract_path_value
from .projects import process_project_details
from utils import multi_extract_object_reader

TEMPLATE = """
## Overview
* Number of Instances: {instance_count}
* Total Projects: {project_count}
* Total Lines of Code: {lines_of_code}

## Instances
| Server ID | Url | Version | Projects | Lines of Code | Users | SAST Configured |
|:----------|:----|:--------|:---------|:--------------|:------|:----------------|
{instances}
"""


def process_server_details(directory, extract_mapping):
    details = list()

    for url, server_details in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                           key='getServerInfo'):
        details.append(
            dict(
                url=url,
                server_id=extract_path_value(obj=server_details, path='System.Server ID'),
                version=extract_path_value(obj=server_details, path='System.Version'),
                edition=extract_path_value(obj=server_details, path='System.Edition'),
                lines_of_code=extract_path_value(obj=server_details, path='System.Lines of Code', default=0),
            )
        )
    return details


def generate_sast_default():
    return False


def process_sast_config(directory, extract_mapping, server_id_mapping):
    servers = defaultdict(generate_sast_default)
    for url, setting in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getProjectSettings'):
        if 'security.conf' in setting['key'].lower():
            servers[server_id_mapping[url]] = True
    return servers


def process_user_totals(directory, extract_mapping, server_id_mapping):
    server_users = defaultdict(int)
    for url, user in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getUsers'):
        server_id = server_id_mapping[url]
        server_users[server_id] = extract_path_value(obj=user, path='$.paging.total')
    return server_users


def generate_server_markdown(directory, extract_mapping):
    server_details = process_server_details(directory=directory, extract_mapping=extract_mapping)
    id_map = {
        server['url']: server['server_id'] for server in server_details
    }
    projects = process_project_details(directory=directory, extract_mapping=extract_mapping, server_id_mapping=id_map)
    user_totals = process_user_totals(directory=directory, extract_mapping=extract_mapping, server_id_mapping=id_map)
    sast_configs = process_sast_config(directory=directory, extract_mapping=extract_mapping, server_id_mapping=id_map)
    return TEMPLATE.format(
        instance_count=len(server_details),
        project_count=sum([len(projects[server['server_id']]) for server in server_details]),
        lines_of_code=sum([int(0 if not server.get('lines_of_code') else server.get('lines_of_code')) for server in server_details]),
        instances="\n".join(
            [
                f"| {server['server_id']} | {server['url']} | {server['version']} | {len(projects[server['server_id']])} | {server['lines_of_code']} | {user_totals[server['server_id']]} | {sast_configs[server['server_id']]} |"
                for server in server_details])
    ), id_map, projects
