from collections import defaultdict

from parser import extract_path_value
from report.utils import generate_section
from utils import multi_extract_object_reader


def process_quality_gates(directory, extract_mapping, server_id_mapping, projects):
    quality_gates = defaultdict(lambda: defaultdict(lambda: dict(
        server_id=None,
        name=None,
        is_built_in=False,
        is_default=False,
        is_cayc=False,
        new_duplicated_lines_density=False,
        new_coverage=False,
        new_security_hotspots_reviewed=False,
        new_violations=False,
        other=False,
        conditions=list(),
        projects=list(),
        project_count=0
    )))
    for url, quality_gate in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                         key='getGates'):
        server_id = server_id_mapping[url]
        name = extract_path_value(obj=quality_gate, path='$.name')
        is_built_in = extract_path_value(obj=quality_gate, path='$.isBuiltIn', default=False)
        if not name:
            continue
        quality_gates[server_id][name]['server_id'] = server_id
        quality_gates[server_id][name]['name'] = name
        quality_gates[server_id][name]['is_built_in'] = is_built_in
        quality_gates[server_id][name]['is_default'] = extract_path_value(obj=quality_gate, path='$.isDefault', default=False)
        quality_gates[server_id][name]['is_cayc'] = extract_path_value(obj=quality_gate, path='$.caycStatus') in ('compliant', 'over-compliant')
        quality_gates[server_id][name]['new_duplicated_lines_density'] = is_built_in
        quality_gates[server_id][name]['new_coverage'] = is_built_in
        quality_gates[server_id][name]['new_security_hotspots_reviewed'] = is_built_in
        quality_gates[server_id][name]['new_violations'] = is_built_in
        quality_gates[server_id][name]['other'] = name == 'Sonar way for AI Code'
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
            sort_order='desc', filter_lambda=lambda x: x['project_count'] > 0 or x['is_default'],
            rows=quality_gates,
        ),
        generate_section(
            headers_mapping={"Server ID": "server_id", "Quality Gate Name": "name"},
            title='Unused Custom Quality Gates', level=3,
            filter_lambda=lambda x: x['project_count'] == 0 and x['is_default'],
            rows=quality_gates,
        )
    )

def process_gate_conditions(directory, extract_mapping, server_id_mapping, gates):
    for url, condition in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                      key='getGateConditions'):

        server_id = server_id_mapping[url]
        gate_name = extract_path_value(obj=condition, path='$.gateName')
        metric = extract_path_value(obj=condition, path='$.metric')
        if gate_name not in gates[server_id]:
            continue
        if metric in gates[server_id][gate_name]:
            gates[server_id][gate_name][metric] = True
        else:
            gates[server_id][condition['gateName']]['other'] = True
    return gates