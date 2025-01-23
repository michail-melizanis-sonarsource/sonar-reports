from collections import defaultdict

from report.utils import generate_section
from utils import multi_extract_object_reader


def process_quality_gates(directory, extract_mapping, server_id_mapping, projects):
    quality_gates = defaultdict(dict)
    for url, quality_gate in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                         key='getGates'):
        server_id = server_id_mapping[url]
        quality_gates[server_id][quality_gate['name']] = dict(
            server_id=server_id,
            name=quality_gate['name'],
            is_built_in="Yes" if quality_gate.get('isBuiltIn', False) else "No",
            is_default="Yes" if quality_gate.get('isDefault', False) else "No",
            project_count=0
        )
    for server_id, project_list in projects.items():
        for project in project_list:
            quality_gates[server_id][project['quality_gate']]['project_count'] += 1
    return [v for k, v in quality_gates.items() for k, v in v.items()]


def generate_gate_markdown(directory, extract_mapping, server_id_mapping, projects):
    quality_gates = process_quality_gates(directory=directory, extract_mapping=extract_mapping,
                                          server_id_mapping=server_id_mapping, projects=projects)


    return (
        generate_section(
            headers_mapping={"Server ID": "server_id", "Quality Gate Name": "name",
                             "# of Projects using": "project_count",
                             "Is Default": "is_default"},
            title='Active Custom Quality Gates', level=3, sort_by_lambda=lambda x: x['project_count'],
            sort_order='desc', filter_lambda=lambda x: x['project_count'] > 0 or x['is_default'] == "Yes",
            rows=quality_gates,
        ),
        generate_section(
            headers_mapping={"Server ID": "server_id", "Quality Gate Name": "name"},
            title='Unused Custom Quality Gates', level=3,
            filter_lambda=lambda x: x['project_count'] == 0 and x['is_default'] != "Yes",
            rows=quality_gates,
        )
    )
