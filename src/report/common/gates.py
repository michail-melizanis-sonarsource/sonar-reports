from collections import defaultdict

from utils import multi_extract_object_reader

ACTIVE_TEMPLATE = """
### Active Custom Quality Gates
| Server ID  | Quality Gate Name | # of Projects using | Is Default |
|:-----------|:------------------|:--------------------|:-----------|
{active_quality_gates}
"""

INACTIVE_TEMPLATE = """
### Unused Custom Quality Gates
| Server ID | Quality Gate Name |
|:----------|:------------------|
{inactive_quality_gates}
"""


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


def format_active_quality_gates(quality_gates):
    return "\n".join([
        "| {server_id} | {name} | {project_count} | {is_default} |".format(**gate)
        for gate in sorted(quality_gates, key=lambda x: x['project_count'], reverse=True) if
        (gate['project_count'] > 0 or gate['is_default'] == "Yes") and gate['is_built_in'] != "Yes"
    ])


def format_inactive_quality_gates(quality_gates):
    return "\n".join([
        "| {server_id} | {name} |".format(**gate)
        for gate in quality_gates if gate['project_count'] == 0 and gate['is_default'] != "Yes" and gate['is_built_in'] != "Yes"
    ])


def generate_gate_markdown(directory, extract_mapping, server_id_mapping, projects):
    quality_gates = process_quality_gates(directory=directory, extract_mapping=extract_mapping,
                                          server_id_mapping=server_id_mapping, projects=projects)
    return (
        ACTIVE_TEMPLATE.format(
            active_quality_gates=format_active_quality_gates(quality_gates=quality_gates)
        ),
        INACTIVE_TEMPLATE.format(
            inactive_quality_gates=format_inactive_quality_gates(quality_gates=quality_gates)
        )
    )
