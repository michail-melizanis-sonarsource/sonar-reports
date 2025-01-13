from collections import defaultdict

from utils import multi_extract_object_reader

TEMPLATE = """
### Permission Templates
| Server ID  | Template Name | Description | Project key pattern | Default For |
|:-----------|:--------------|:------------|:--------------------|:------------|
{permission_templates}"""


def process_permission_templates(directory, extract_mapping, server_id_mapping):
    default_templates = defaultdict(dict)
    MAPPING = dict(
        APP="Applications",
        TRK="Projects",
        VW="Portfolios"
    )
    for url, template in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getDefaultTemplates'):
        server_id = server_id_mapping[url]
        if template['templateId'] not in default_templates[server_id].keys():
            default_templates[server_id][template['templateId']] = set()
        default_templates[server_id][template['templateId']].add(MAPPING[template['qualifier']])
    templates = list()
    for url, template in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                     key='getTemplates'):
        server_id = server_id_mapping[url]
        templates.append(
            dict(
                server_id=server_id,
                name=template['name'],
                description=template.get('description', ""),
                pattern=template.get('projectKeyPattern', ""),
                defaults=", ".join(default_templates[server_id].get(template['id'], []))
            )
        )
    return templates


def format_permission_templates(permission_templates):
    return "\n".join(
        [
            "| {server_id} | {name} | {description} | {pattern} | {defaults} |".format(**template)
            for template in permission_templates
        ]
    )


def generate_permission_template_markdown(directory, extract_mapping, server_id_mapping):
    permission_templates = process_permission_templates(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)

    return TEMPLATE.format(
        permission_templates=format_permission_templates(permission_templates=permission_templates)
    )
