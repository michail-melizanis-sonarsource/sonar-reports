from collections import defaultdict

from utils import multi_extract_object_reader
from parser import extract_path_value

TEMPLATE = """
## Project Metrics
| Server ID | Project Name | Total Rules | Template Rules | Plugin Rules |
|:----------|:-------------|:------------|:---------------|:-------------|
{projects}
"""


def process_project_details(directory, extract_mapping, server_id_mapping):
    projects = defaultdict(list)
    for url, project in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getProjectDetails'):
        server_id = server_id_mapping[url]
        projects[server_id].append(
            dict(
                server_id=server_id,
                name=project['name'],
                key=project['key'],
                main_branch=project.get('branch', ''),
                profiles=[i['key'] for i in project['qualityProfiles'] if not i.get('deleted', False)],
                languages=set([i['language'] for i in project['qualityProfiles'] if not i.get('deleted', False)]),
                quality_gate=project['qualityGate']['name'],
                binding=project.get('binding', dict()).get('key', ''),
                rules=0,
                template_rules=0,
                plugin_rules=0
            )
        )
    return projects


def process_project_branches(directory, extract_mapping, server_id_mapping):
    branches = defaultdict(dict)
    for url, branch in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getBranches'):
        server_id = server_id_mapping[url]
        if not branch.get('excludedFromPurge'):
            continue
        if branch['projectKey'] not in branches[server_id].keys():
            branches[server_id][branch['projectKey']] = set()
        branches[server_id][branch['projectKey']].add(branch['name'])
    return {k: {p for p, b in v.items() if len(b) > 1} for k, v in branches.items()}


def process_project_pull_requests(directory, extract_mapping, server_id_mapping):
    projects = defaultdict(dict)
    for url, pull_request in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                         key='getProjectPullRequests'):
        server_id = server_id_mapping[url]
        if pull_request['projectKey'] not in projects[server_id].keys():
            projects[server_id][pull_request['projectKey']] = 0
        projects[server_id][pull_request['projectKey']] +=1
    return {server_id: {k for k, v in projects.items() if v > 0} for server_id, projects in projects.items()}


def format_project_metrics(projects):
    return "\n".join(
        [
            f"| {server_id} | {project['name']} | {project['rules']} | {project['template_rules']} | {project['plugin_rules']} |"
            for server_id, project_list in projects.items()
            for project in project_list if project['template_rules'] > 0 or project['plugin_rules'] > 0
        ]
    )


def generate_project_metrics_markdown(projects):
    return TEMPLATE.format(projects=format_project_metrics(projects=projects))
