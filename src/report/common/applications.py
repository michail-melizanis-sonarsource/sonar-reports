from utils import multi_extract_object_reader
ACTIVE_TEMPLATE = """### Active Applications
| Server ID | Application Name | # Projects |
|:----------|:-----------------|:------------|
{active_applications}
"""

INACTIVE_TEMPLATE = """
### Inactive Applications
| Server ID | Application Name |
|:----------|:-----------------|
{inactive_applications}
"""


def process_applications(directory, extract_mapping, server_id_mapping):
    applications = list()
    for url, application in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                        key='getApplicationDetails'):
        server_id = server_id_mapping[url]
        if 'application' in application.keys():
            application= application['application']
        applications.append(
            dict(
                server_id=server_id,
                name=application['name'],
                project_count=len(application['projects'])
            )
        )
    return applications

def format_active_applications(applications):
    return "\n".join(
        ["| {server_id} | {name} | {project_count} |".format(
            server_id=application['server_id'],
            name=application['name'],
            project_count=application['project_count']
        ) for application in applications if application['project_count'] > 0])

def format_inactive_applications(applications):
    return "\n".join(
        ["| {server_id} | {name} |".format(
            server_id=application['server_id'],
            name=application['name'],
        ) for application in applications if application['project_count'] == 0]
    )


def generate_application_markdown(directory, extract_mapping, server_id_mapping):
    applications = process_applications(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    active_applications = format_active_applications(applications)
    inactive_applications = format_inactive_applications(applications)
    return ACTIVE_TEMPLATE.format(active_applications=active_applications), INACTIVE_TEMPLATE.format(inactive_applications=inactive_applications)
