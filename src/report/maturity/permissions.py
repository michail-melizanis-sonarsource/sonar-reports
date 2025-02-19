from collections import defaultdict

from parser import extract_path_value
from report.utils import generate_section
from utils import multi_extract_object_reader


def process_global_permissions(extract_directory, extract_mapping):
    permissions = {
        'user': defaultdict(int),
        'groups': defaultdict(int)
    }
    for key in permissions.keys():
        for url, entity in multi_extract_object_reader(directory=extract_directory, mapping=extract_mapping,
                                                       key=f"get{key.capitalize()}{'Permissions' if key == 'user' else ''}"):
            for permission in extract_path_value(obj=entity, path='$.permissions', default=list()):
                permissions[key][permission] += 1
    return permissions

def process_entity_permissions(extract_directory, extract_mapping):
    permissions = {
        "profile": {
            'users': set(),
            'groups': set()
        },
        "gate": {
            'users': set(),
            'groups': set()
        }

    }
    for entity_type, perms in permissions.items():
        for key in perms.keys():
            for url, entity in multi_extract_object_reader(directory=extract_directory, mapping=extract_mapping,
                                                           key=f"get{entity_type.capitalize()}{key.capitalize()}"):
                path_key = 'login' if key == 'user' else 'name'
                permissions[entity_type][key].add(extract_path_value(obj=entity, path=f'$.{path_key}'))
    return permissions

def generate_permissions_markdown(extract_directory, extract_mapping):
    global_permissions = process_global_permissions(extract_directory=extract_directory, extract_mapping=extract_mapping)
    specific_permissions = process_entity_permissions(extract_directory=extract_directory, extract_mapping=extract_mapping)

    row = dict(
        global_user_profile=global_permissions['user']['profileadmin'],
        global_user_quality_gate=global_permissions['user']['gateadmin'],
        global_group_profile=global_permissions['groups']['profileadmin'],
        global_group_quality_gate=global_permissions['groups']['profileadmin'],
        specific_user_profile=len(specific_permissions["profile"]['users']),
        specific_user_quality_gate=len(specific_permissions["gate"]['users']),
        specific_group_profile=len(specific_permissions["profile"]['groups']),
        specific_group_quality_gate=len(specific_permissions["gate"]['groups'])
    )

    return generate_section(
        headers_mapping={
            "Users with Global Profile Admin Permission": "global_user_profile",
            "Users with Global Quality Gate Admin Permission": "global_user_quality_gate",
            "Groups with Global Profile Admin Permission": "global_group_profile",
            "Groups with Global Quality Gate Admin Permission": "global_group_quality_gate",
            "Users with Edit Permission on Specific Profiles": "specific_user_profile",
            "Users with Edit Permission on Specific Quality Gates": "specific_user_quality_gate",
            "Groups with Edit Permission on Specific Profiles": "specific_group_profile",
            "Groups with Edit Permission on Specific Quality Gates": "specific_group_quality_gate"
        },
        level=3,
        rows=[row],
        title="Quality Governance Permissions",
    ), global_permissions
