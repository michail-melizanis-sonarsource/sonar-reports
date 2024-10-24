from collections import defaultdict
import os
import csv
from utils import object_reader


def is_cloud_binding(binding):
    is_cloud = False
    cloud_endpoints = ['dev.azure.com', 'gitlab.com', 'api.github.com', 'bitbucket.org']
    if any([endpoint in binding.get('url', '') for endpoint in cloud_endpoints]):
        is_cloud = True
    return is_cloud


def create_default_org():
    return dict(
        key='',
        alm=None,
        is_cloud=False,
        url='',
        projects=[],
    )


def generate_org_structure(export_directory):
    projects = list(object_reader(directory=export_directory, key='getProjects'))
    project_repos = {i['projectKey']: i for i in object_reader(directory=export_directory, key='getProjectBindings')}
    bindings = {i['key']: i for i in object_reader(directory=export_directory, key='getBindings')}
    organizations = defaultdict(create_default_org)
    for project in projects:
        project_key = project['key']
        project_binding = project_repos.get(project_key, dict(key='default'))
        binding = bindings.get(project_binding['key'], dict())
        org_key = project_binding['key']
        organizations[org_key]['sonarqube_org_key'] = org_key
        organizations[org_key]['alm'] = project_binding.get('alm')
        organizations[org_key]['url'] = binding.get('url')
        organizations[org_key]['is_cloud'] = is_cloud_binding(binding)
        organizations[org_key]['projects'].append(
            dict(
                sonarqube_org_key=org_key,
                project_key=project_key,
                project_name=project['name'],
                repository=project_binding.get('repository'),
                is_monorepo=project_binding.get('monorepo', False),
                summary_comment_enabled=project_binding.get('summaryCommentEnabled', False),
            )
        )
    org_file_path = os.path.join(export_directory, 'organizations.csv')
    with open(org_file_path, 'wt') as f:
        writer = csv.DictWriter(f, fieldnames=['sonarqube_org_key', 'sonarcloud_org_key', 'alm', 'is_cloud', 'url', 'num_projects'], extrasaction='ignore')
        writer.writeheader()
        for org in organizations.values():
            writer.writerow(dict(**org, num_projects=len(org['projects'])))

    with open(os.path.join(export_directory, 'projects.csv'), 'wt') as f:
        writer = csv.DictWriter(f, fieldnames=['sonarqube_org_key', 'project_key', 'project_name', 'repository', 'is_monorepo', 'summary_comment_enabled'], extrasaction='ignore')
        writer.writeheader()
        for org in organizations.values():
            for project in org['projects']:
                writer.writerow(project)
    return org_file_path

