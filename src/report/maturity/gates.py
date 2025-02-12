from report.common.gates import process_gate_conditions, process_quality_gates
from report.utils import generate_section


def generate_gate_maturity_markdown(directory, extract_mapping, server_id_mapping, projects):
    gates = process_quality_gates(directory=directory, extract_mapping=extract_mapping,
                                  server_id_mapping=server_id_mapping, projects=projects)
    gates = process_gate_conditions(directory=directory, extract_mapping=extract_mapping,
                                              server_id_mapping=server_id_mapping, gates=gates)
    summary_row = dict(
        gates=sum(len(i) for i in gates.values()),
        active=sum([1 for server_gates in gates.values() for gate in server_gates.values() if gate['project_count'] > 0 or gate['is_default'] == "Yes"]),
        cayc=sum([1 for server_gates in gates.values() for gate in server_gates.values() if gate['is_cayc'] ]),
        issue='',

    )
    summary = generate_section(
        headers_mapping={
            "Total Gates": "gates",
            "Active Gates": "active",
            "CaYC Compliant Gates": "cayc"
        },
        title='Quality Gate Overview', level=3,
        rows=[summary_row]
    )

    detail_rows = [
        dict(
            server_id=server_id,
            gate_name=key,
            project_count=gate['project_count'],
            is_cayc="Yes" if gate['is_cayc'] else "No",
            issue=gate['new_violations'],
            hotspot=gate['new_security_hotspots_reviewed'],
            coverage=gate['new_coverage'],
            duplication=gate['new_duplicated_lines_density'],
            other=gate['other']
        )
        for server_id, server_gates in gates.items() for key, gate in server_gates.items() if gate['project_count'] > 0 or gate['is_default'] == "Yes"
    ]

    details = generate_section(
        headers_mapping={
            "Server ID": "server_id",
            "Quality Gate Name": "gate_name",
            "# of Projects using": "project_count",
            "CaYC Compliant": "is_cayc",
            "New Issue Rule": "issue",
            "Hotspot Rule": "hotspot",
            "Coverage Rule": "coverage",
            "Duplication Rule": "duplication",
            "Other Rules": "other"
            },
        title='Active Quality Gates', level=3,
        rows=detail_rows
    )
    return summary, details
