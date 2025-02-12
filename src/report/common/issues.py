from collections import defaultdict
from utils import multi_extract_object_reader

def process_fixed_issues(directory, extract_mapping, server_id_mapping):
    issues = defaultdict(int)
    for url, measure in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getMeasures'):
        server_id = server_id_mapping[url]
        if measure['metric'] == 'reliability_remediation_effort':
            issues[server_id] += measure['value']
    return issues

def generate_issues_markdown(measures):
    row = dict(
        total_issues=0,
        new_reliability_issues=0,
        new_vulnerabilities=0,
        new_maintainability_issues=0,
        projects_with_new_issues=0,
        resolved_issues=0
    )