from collections import defaultdict

from .projects import process_project_pull_requests, process_project_branches
from utils import multi_extract_object_reader
from parser import extract_path_value

TEMPLATE = """
## DevOps Integrations
| Server ID | DevOps Platform Binding  | Type | URL | # Projects | Multi-branch Projects? | PR Projects? |
|:----------|:-------------------------|:-----|:----|:------------|:-----------------------|:-------------|
{devops_bindings}
"""


def process_project_bindings(directory, extract_mapping, server_id_mapping):
    devops_bindings = defaultdict(dict)
    for url, project_binding in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                            key='getProjectBindings'):
        server_id = server_id_mapping[url]
        if project_binding['key'] not in devops_bindings[server_id].keys():
            devops_bindings[server_id][project_binding['key']] = dict(
                projects=set(),
                name=project_binding['key'],
                type=project_binding['alm']
            )
        devops_bindings[server_id][project_binding['key']]['projects'].add(project_binding['projectKey'])
    return devops_bindings


def process_devops_bindings(directory, extract_mapping, server_id_mapping):
    bindings = defaultdict(list)
    for url, binding in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getBindings'):
        server_id = server_id_mapping[url]
        bindings[server_id].append(
            dict(
                key=binding['key'],
                alm=binding['alm'],
                url=binding['url']
            )
        )
    return bindings


def format_bindings(bindings):
    return "\n".join(
        [
            f"| {binding['server_id']} | {binding['binding']} | {binding['type']} | {binding['url']}| {binding['projects']} | {binding['multi_branch_projects']} | {binding['pr_projects']} |"
            for binding in sorted(bindings, key=lambda x: x['projects'], reverse=True)
        ]
    )


def generate_devops_markdown(directory, extract_mapping, server_id_mapping):
    bindings = list()
    project_bindings = process_project_bindings(directory=directory, extract_mapping=extract_mapping,
                                                server_id_mapping=server_id_mapping)
    devops_bindings = process_devops_bindings(directory=directory, extract_mapping=extract_mapping,
                                              server_id_mapping=server_id_mapping)
    branches = process_project_branches(directory=directory, extract_mapping=extract_mapping,
                                        server_id_mapping=server_id_mapping)
    pull_requests = process_project_pull_requests(directory=directory, extract_mapping=extract_mapping,
                                                  server_id_mapping=server_id_mapping)
    for server_id, dev_bindings in devops_bindings.items():
        for devops_binding in dev_bindings:
            project_data = project_bindings[server_id].get(devops_binding['key'], dict()).get('projects', set())
            binding = dict(
                server_id=server_id,
                binding=devops_binding['key'],
                type=devops_binding['alm'],
                url=devops_binding['url'],
                projects=len(project_data),
                multi_branch_projects='Yes' if project_data & branches.get(server_id, set()) else 'No',
                pr_projects='Yes' if project_data & pull_requests.get(server_id, set()) else 'No'
            )
            bindings.append(binding)
    return TEMPLATE.format(devops_bindings=format_bindings(bindings=bindings))
