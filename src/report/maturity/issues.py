from collections import defaultdict

from report.utils import generate_section
from utils import multi_extract_object_reader

FOLDER_MAPPING = dict(resolved='getProjectResolvedIssueTypes', all='getProjectIssueTypes',
                      recent='getProjectRecentIssueTypes')


def process_issues(extract_directory, extract_mapping, server_id_mapping):
    project_issues = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for setting, key in FOLDER_MAPPING.items():
        for url, issues in multi_extract_object_reader(directory=extract_directory, mapping=extract_mapping, key=key):
            server_id = server_id_mapping[url]
            project = project_issues[server_id][issues['projectKey']]
            if issues['severity'] not in project:
                project[issues['issueType']][issues['severity']] = dict(
                    project_key=issues['projectKey'],
                    issue_type=issues['issueType'],
                    server_id=server_id,
                    severity=issues['severity'],
                    all=0,
                    open=0,
                    fixed=0,
                    wontfix=0,
                    removed=0,
                    false_positive=0,
                    recent=0
                )
            issue_count = issues.get('total', 0)
            if setting == 'resolved':
                resolution = issues['resolution'].lower().replace('-', "_")
                project[issues['issueType']][issues['severity']][resolution] = issue_count
                project[issues['issueType']][issues['severity']]['open'] -= issue_count
            else:
                project[issues['issueType']][issues['severity']][setting] = issue_count
                if setting == 'all':
                    project[issues['issueType']][issues['severity']]['open'] += issue_count
    return project_issues


def generate_issue_markdown(extract_directory, extract_mapping, server_id_mapping):
    project_issues = process_issues(extract_directory=extract_directory, extract_mapping=extract_mapping,
                                    server_id_mapping=server_id_mapping)
    issue_rows = {
        severity: {
            "severity": severity,
            "open_vulnerabilities": 0,
            "open_bugs": 0,
            "open_code_smells": 0,
            "recent_vulnerabilities": 0,
            "recent_bugs": 0,
            "recent_code_smells": 0,
            "affected_projects": set(),
            "project_count": 0

        } for severity in ['BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR', 'INFO']
    }
    detail_rows = {
        issue_type: {severity: {
            "severity": severity,
            "open": 0,
            "recent": 0,
            "fixed": 0,
            "wontfix": 0,
            "false_positive": 0,
            "affected_projects": set(),
            "project_count": 0

        } for severity in ['BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR', 'INFO']
        } for issue_type in ['CODE_SMELL', 'BUG', 'VULNERABILITY']
    }

    for server_id, issues in project_issues.items():
        for project_key, issue_types in issues.items():
            for issue_type, severities in issue_types.items():
                for severity, issue in severities.items():
                    detail_rows[issue_type][severity]['open'] += issue['open']
                    detail_rows[issue_type][severity]['recent'] += issue['recent']
                    detail_rows[issue_type][severity]['fixed'] += issue['fixed']
                    detail_rows[issue_type][severity]['wontfix'] += issue['wontfix']
                    detail_rows[issue_type][severity]['false_positive'] += issue['false_positive']
                    if issue['open'] > 0:
                        detail_rows[issue_type][severity]['affected_projects'].add(issue['project_key'])
                        detail_rows[issue_type][severity]['project_count'] = len(detail_rows[issue_type][severity]['affected_projects'])
                        issue_rows[severity]['affected_projects'].add(issue['project_key'])
                        issue_rows[severity]['project_count'] = len(issue_rows[severity]['affected_projects'])

                    if issue_type == 'VULNERABILITY':
                        issue_rows[severity]['open_vulnerabilities'] += issue['open']
                        issue_rows[severity]['recent_vulnerabilities'] += issue['recent']
                    elif issue_type == 'BUG':
                        issue_rows[severity]['open_bugs'] += issue['open']
                        issue_rows[severity]['recent_bugs'] += issue['recent']
                    elif issue_type == 'CODE_SMELL':
                        issue_rows[severity]['open_code_smells'] += issue['open']
                        issue_rows[severity]['recent_code_smells'] += issue['recent']


    overview_md = generate_section(
        title='Issues Overview',
        level=3,
        headers_mapping={
            "Severity": "severity",
            "Open Vulnerabilities": "open_vulnerabilities",
            "Open Bugs": "open_bugs",
            "Open Code Smells": "open_code_smells",
            "Recent Vulnerabilities": "recent_vulnerabilities",
            "Recent Bugs": "recent_bugs",
            "Recent Code Smells": "recent_code_smells",
            "Affected Projects": "project_count",
        },
        rows=issue_rows.values()
    )
    vulnerability_md = generate_section(
        title='Vulnerabilities',
        level=3,
        headers_mapping={
            "Severity": "severity",
            "Open": "open",
            "Recent": "recent",
            "Fixed": "fixed",
            "Won't Fix": "wontfix",
            "False Positive": "false_positive",
            "Affected Projects": "project_count",
        },
        rows=detail_rows['VULNERABILITY'].values()
    )
    bug_md = generate_section(
        title='Bugs',
        level=3,
        headers_mapping={
            "Severity": "severity",
            "Open": "open",
            "Recent": "recent",
            "Fixed": "fixed",
            "Won't Fix": "wontfix",
            "False Positive": "false_positive",
            "Affected Projects": "project_count",
        },
        rows=detail_rows['BUG'].values()
    )
    code_smell_md = generate_section(
        title='Code Smells',
        level=3,
        headers_mapping={
            "Severity": "severity",
            "Open": "open",
            "Recent": "recent",
            "Fixed": "fixed",
            "Won't Fix": "wontfix",
            "False Positive": "false_positive",
            "Affected Projects": "project_count",
        },
        rows=detail_rows['CODE_SMELL'].values()
    )
    return overview_md, vulnerability_md, bug_md, code_smell_md
