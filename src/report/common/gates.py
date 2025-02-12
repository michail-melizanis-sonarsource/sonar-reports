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
            is_cayc=True if quality_gate.get('caycStatus', '') in ('compliant', 'over-compliant') else False,
            new_duplicated_lines_density="Yes" if quality_gate.get('isBuiltIn', False) else "No",
            new_coverage="Yes" if quality_gate.get('isBuiltIn', False) else "No",
            new_security_hotspots_reviewed="Yes" if quality_gate.get('isBuiltIn', False) else "No",
            new_violations="Yes" if quality_gate.get('isBuiltIn', False) else "No",
            other="No" if quality_gate['name'] !='Sonar way for AI Code' else "Yes",
            conditions=[],
            project_count=0
        )
    for server_id, server_projects in projects.items():
        for project in server_projects.values():
            quality_gates[server_id][project['quality_gate']]['project_count'] += 1
    return quality_gates


def generate_gate_markdown(directory, extract_mapping, server_id_mapping, projects):
    quality_gates = process_quality_gates(directory=directory, extract_mapping=extract_mapping,
                                          server_id_mapping=server_id_mapping, projects=projects)

    quality_gates = [v for k, v in quality_gates.items() for k, v in v.items()]
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

def process_gate_conditions(directory, extract_mapping, server_id_mapping, gates):
    for url, condition in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                      key='getGateConditions'):

        server_id = server_id_mapping[url]
        if condition['gateName'] not in gates[server_id]:
            continue
        if condition['metric'] in gates[server_id][condition['gateName']]:
            gates[server_id][condition['gateName']][condition['metric']] = "Yes"
        else:
            gates[server_id][condition['gateName']]['other'] = "Yes"
    return gates