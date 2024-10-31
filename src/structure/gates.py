from utils import multi_extract_object_reader


def map_gates(project_org_mapping, extract_mapping, export_directory):
    results = dict()
    gates = {
        server_url + gate['name']: gate for server_url, gate in
        multi_extract_object_reader(directory=export_directory, mapping=extract_mapping, key='getGates') if
        not gate['isBuiltIn']
    }
    for server_url, project_details in multi_extract_object_reader(directory=export_directory, mapping=extract_mapping,
                                                                   key='getProjectDetails'):
        org_key = project_org_mapping.get(server_url + project_details['projectKey'])
        if not project_details.get('qualityGate') or not org_key:
            continue
        gate_key = server_url + project_details['qualityGate']['name']
        unique_key = org_key + project_details['qualityGate']['name']
        if gate_key in gates.keys():
            results[unique_key] = dict(
                name=project_details['qualityGate']['name'],
                server_url=project_details['serverUrl'],
                source_gate_key=project_details['qualityGate']['name'],
                is_default=gates[gate_key]['isDefault'],
                sonarqube_org_key=org_key
            )
    for org_key in set(project_org_mapping.values()):
        for gate in gates.values():
            if not gate['isDefault']:
                continue
            unique_key = org_key + gate['name']
            results[unique_key] = dict(
                name=gate['name'],
                server_url=gate['serverUrl'],
                source_gate_key=gate['name'],
                is_default=True,
                sonarqube_org_key=org_key
            )
    return list(results.values())
