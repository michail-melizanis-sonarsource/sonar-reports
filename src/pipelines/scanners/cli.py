from parser import extract_path_value
from pipelines.scanners.base import get_mappings


def get_config_file_name():
    return 'sonar-project.properties',

def update_content(content, projects:set, project_mappings):
    mapping = get_mappings()
    updated_keys = set()
    updated_content = list()
    for i in content.splitlines():
        val = i
        key = i.split('=')[0]
        if key in mapping:
            for project in projects:
                if project in project_mappings:
                    val = format_value(key=key, path=mapping[key], project=project_mappings[project])
                    updated_keys.add(key)
        updated_content.append(val)
    for key, path in mapping.items():
        if key not in updated_keys:
            val = ""
            for project in projects:
                if project in project_mappings:
                    val = format_value(key=key, path=path, project=project_mappings[project])
            updated_content.append(val)

    return dict(updated_content="\n".join(updated_content), is_updated=True)

def format_value(key, path, project):
    return f"{key}={extract_path_value(project, path=path, default='')}"