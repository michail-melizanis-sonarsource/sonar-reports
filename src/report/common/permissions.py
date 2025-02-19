from collections import defaultdict

from parser import extract_path_value
from report.utils import generate_section
from utils import multi_extract_object_reader
import re


def process_permission_templates(directory, extract_mapping, server_id_mapping):
    default_templates = defaultdict(lambda: defaultdict(set))
    MAPPING = dict(
        APP="Applications",
        TRK="Projects",
        VW="Portfolios"
    )
    for url, template in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                     key='getDefaultTemplates'):
        server_id = server_id_mapping[url]
        template_id = extract_path_value(obj=template, path='$.templateId')
        qualifier = extract_path_value(obj=template, path='$.qualifier')
        if template_id is None or qualifier is None:
            continue
        default_templates[server_id][template_id].add(MAPPING[qualifier])
    templates = list()
    for url, template in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                     key='getTemplates'):
        server_id = server_id_mapping[url]
        templates.append(
            dict(
                server_id=server_id,
                name=extract_path_value(obj=template, path='$.name'),
                description=extract_path_value(obj=template, path='$.description'),
                pattern=extract_path_value(obj=template, path='$.projectKeyPattern'),
                defaults=", ".join(default_templates[server_id].get(template['id'], [])),
                projects=[],
                project_count=0
            )
        )
    return templates


def filter_projects(projects, permission_templates):
    remaining_projects = {server_id: {i['key'] for i in p.values()} for server_id, p in projects.items()}
    for template in permission_templates:
        if template['pattern']:
            try:
                template['projects'] = [project for project in projects[template['server_id']].values() if
                                        re.match(template['pattern'], project['key'])]
                remaining_projects[template['server_id']] -= {i['key'] for i in template['projects']}
                template['project_count'] = len(template['projects'])
            except re.error:
                template['projects'] = []
                template['project_count'] = 0
    for template in permission_templates:
        if 'Projects' in template['defaults']:
            template['projects'] = remaining_projects[template['server_id']]
            template['project_count']= len(template['projects'])
    return permission_templates


def generate_permission_template_markdown(directory, extract_mapping, server_id_mapping, projects, only_active=False):
    permission_templates = process_permission_templates(directory=directory, extract_mapping=extract_mapping,
                                                        server_id_mapping=server_id_mapping)

    permission_templates = filter_projects(projects=projects, permission_templates=permission_templates)
    return generate_section(
        headers_mapping={
            "Server ID": "server_id",
            "Template Name": "name",
            "Description": "description",
            "Project key pattern": "pattern",
            "Default For": "defaults",
            "Projects": "project_count"
        },
        level=3,
        rows=permission_templates,
        title="Permission Templates",
        filter_lambda=lambda x: x['project_count'] > 0 or not only_active

    ), permission_templates
