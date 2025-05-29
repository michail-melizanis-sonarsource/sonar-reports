from collections import defaultdict

from parser import extract_path_value
from utils import multi_extract_object_reader


def add_group_result(results, org_key, name, server_url, description=None):
    unique_key = org_key + name
    results[unique_key] = dict(
        name=name,
        server_url=server_url,
        description=description,
        sonarqube_org_key=org_key,
    )
    return results


def add_default_groups(results, project_org_mapping, export_directory, extract_mapping):
    org_keys = set(project_org_mapping.values())
    for server_url, group in multi_extract_object_reader(directory=export_directory, mapping=extract_mapping,
                                                         key='getGroups'):
        group_id = extract_path_value(group, '$.id')
        name = extract_path_value(group, '$.name')
        permissions = extract_path_value(group, '$.permissions')
        description = extract_path_value(group, '$.description')
        if any([group_id == 'Anyone', name== 'Anyone']) or not permissions:
            continue
        for org_key in org_keys:
            results = add_group_result(results=results, name=name, org_key=org_key,
                                       server_url=server_url, description=description)
    return results


def add_project_groups(results, export_directory, extract_mapping, project_org_mapping):
    for server_url, group in multi_extract_object_reader(directory=export_directory, mapping=extract_mapping,
                                                         key='getProjectGroupsPermissions'):
        org_key = project_org_mapping.get(server_url + group['project'])
        if not org_key:
            continue
        add_group_result(results=results, name=group['name'],
                         org_key=org_key,
                         server_url=server_url, description=group.get('description'))
    return results


def add_template_groups(results, templates, export_directory, extract_mapping):
    template_orgs = {template['server_url'] + template['source_template_key']: template['sonarqube_org_key'] for template in templates}
    for key in ['getTemplateGroupsScanners', 'getTemplateGroupsViewers']:
        for server_url, group in multi_extract_object_reader(directory=export_directory, mapping=extract_mapping,
                                                             key=key):
            org_key = template_orgs.get(server_url + group['templateId'])
            if not org_key:
                continue
            add_group_result(results=results, name=group['name'],
                             org_key=org_key,
                             server_url=server_url, description=group.get('description'))


    return results


def add_profile_groups(results, export_directory, extract_mapping, profiles):
    profile_orgs = defaultdict(set)
    for profile in profiles:
        profile_orgs[profile['source_profile_key']].add(profile['sonarqube_org_key'])

    for server_url, profile_group in multi_extract_object_reader(directory=export_directory, mapping=extract_mapping,
                                                                 key='getProfileGroups'):
        for org_key in profile_orgs.get(profile_group['profileKey'], []):
            results = add_group_result(results=results, name=profile_group['name'], org_key=org_key,
                                       server_url=server_url, description=profile_group.get('description'))
    return results


def map_groups(project_org_mapping, extract_mapping, profiles, templates, export_directory):
    results = add_default_groups(results=dict(), project_org_mapping=project_org_mapping,
                                 export_directory=export_directory, extract_mapping=extract_mapping)
    results = add_project_groups(results=results, export_directory=export_directory, extract_mapping=extract_mapping,
                                 project_org_mapping=project_org_mapping)
    results = add_template_groups(results=results, templates=templates, export_directory=export_directory, extract_mapping=extract_mapping)
    results = add_profile_groups(results=results, export_directory=export_directory, extract_mapping=extract_mapping,
                                 profiles=profiles)

    return list(results.values())
