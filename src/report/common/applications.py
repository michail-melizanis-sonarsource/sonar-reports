from utils import multi_extract_object_reader
from report.utils import generate_section


def process_applications(directory, extract_mapping, server_id_mapping):
    applications = list()
    for url, application in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                        key='getApplicationDetails'):
        server_id = server_id_mapping[url]
        if 'application' in application.keys():
            application = application['application']
        applications.append(
            dict(
                server_id=server_id,
                name=application['name'],
                project_count=len(application['projects'])
            )
        )
    return applications


def generate_application_markdown(directory, extract_mapping, server_id_mapping):
    applications = process_applications(directory=directory, extract_mapping=extract_mapping,
                                        server_id_mapping=server_id_mapping)
    active_applications = generate_section(
        headers_mapping={'Server ID': 'server_id', 'Application Name': 'name', '# Projects': 'project_count'},
        rows=applications, title='Active Applications', level=3, sort_by_lambda=lambda x: x['project_count'],
        sort_order='desc', filter_lambda=lambda x: x['project_count'] > 0)
    inactive_applications = generate_section(
        headers_mapping={'Server ID': 'server_id', 'Application Name': 'name'},
        rows=applications, title='Inactive Applications', level=3, sort_by_lambda=lambda x: x['name'],
        sort_order='asc', filter_lambda=lambda x: x['project_count'] == 0
    )
    return active_applications, inactive_applications