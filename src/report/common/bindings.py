from collections import defaultdict

from .projects import process_project_pull_requests, process_project_branches
from utils import multi_extract_object_reader
from report.utils import generate_section
from parser import extract_path_value


def process_project_bindings(directory, extract_mapping, server_id_mapping):
    devops_bindings = defaultdict(
        lambda: defaultdict(
            lambda: dict(
                projects=set(),
                name=None,
                type=None
            )
        )
    )
    for url, project_binding in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                            key='getProjectBindings'):
        server_id = server_id_mapping[url]
        binding_key = extract_path_value(obj=project_binding, path='$.key')
        project_key = extract_path_value(obj=project_binding, path='$.projectKey')
        devops_bindings[server_id][binding_key]['name'] = binding_key
        devops_bindings[server_id][binding_key]['type'] = extract_path_value(obj=project_binding, path='$.alm')
        devops_bindings[server_id][project_binding['key']]['projects'].add(project_key)
    return devops_bindings


def process_devops_bindings(directory, extract_mapping, server_id_mapping):
    bindings = defaultdict(list)
    for url, binding in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getBindings'):
        server_id = server_id_mapping[url]
        bindings[server_id].append(
            dict(
                key=extract_path_value(obj=binding, path='$.key'),
                alm=extract_path_value(obj=binding, path='$.alm'),
                url=extract_path_value(obj=binding, path='$.url')
            )
        )
    return bindings


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

    return generate_section(
        headers_mapping={'Server ID': 'server_id', 'DevOps Platform Binding': 'binding', 'Type': 'type', 'URL': 'url',
                         '# Projects': 'projects', 'Multi-branch Projects?': 'multi_branch_projects',
                         'PR Projects?': 'pr_projects'},
        rows=bindings, title='DevOps Integrations', level=2, sort_by_lambda=lambda x: x['projects'],
        sort_order='desc', filter_lambda=lambda x: x['projects'] > 0
    ), pull_requests
