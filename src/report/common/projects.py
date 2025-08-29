from collections import defaultdict

from report.utils import generate_section
from utils import multi_extract_object_reader
from parser import extract_path_value
from datetime import datetime, UTC, timedelta

TIERS = dict(
    xl=500000,
    l=100000,
    m=10000,
    s=1000,
    xs=0,
    unknown=0
)


def process_project_details(directory, extract_mapping, server_id_mapping):
    projects = defaultdict(lambda: defaultdict(lambda: dict(
        server_id=None,
        name=None,
        key=None,
        main_branch=None,
        profiles=None,
        languages=None,
        quality_gate=None,
        binding=None,
        loc=0,
        tier='unknown',
        rules=0,
        template_rules=0,
        plugin_rules=0
    )))
    for url, project in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getProjectDetails'):
        server_id = server_id_mapping[url]
        project_key = extract_path_value(obj=project, path='$.key')
        profiles = [
                    profile for profile in
                    extract_path_value(obj=project, path='qualityProfiles') if
                    not extract_path_value(obj=profile, path='$.deleted', default=False)
                ]
        projects[server_id][project_key].update(
            dict(
                server_id=server_id,
                name=extract_path_value(obj=project, path='$.name'),
                key=project_key,
                main_branch=extract_path_value(obj=project, path='$.branch'),
                profiles=[
                    extract_path_value(obj=profile, path='key') for profile in profiles
                ],
                languages=set([extract_path_value(obj=profile, path='$.language') for profile in profiles]),
                quality_gate=extract_path_value(obj=project, path='$.qualityGate.name'),
                binding=extract_path_value(obj=project, path='$.binding.key'),
            )
        )

    projects = process_project_usage(directory=directory, extract_mapping=extract_mapping,
                                     server_id_mapping=server_id_mapping, projects=projects)
    return projects


def process_project_branches(directory, extract_mapping, server_id_mapping):
    branches = defaultdict(lambda: defaultdict(set))
    for url, branch in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getBranches'):
        server_id = server_id_mapping[url]
        excluded = extract_path_value(obj=branch, path='$.excludedFromPurge', default=False)
        project_key = extract_path_value(obj=branch, path='$.projectKey')
        if not excluded:
            continue
        branches[server_id][project_key].add(branch['name'])
    return {k: {p for p, b in v.items() if len(b) > 1} for k, v in branches.items()}


def process_project_pull_requests(directory, extract_mapping, server_id_mapping):
    projects = defaultdict(lambda: defaultdict(lambda: dict(
        pull_requests=0,
        recent_pr_scans=0,
        recent_failed_prs=0
    )))
    now = datetime.now(tz=UTC)
    recent_window_start = now - timedelta(days=30)
    for url, pull_request in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                         key='getProjectPullRequests'):
        server_id = server_id_mapping[url]
        project_key = extract_path_value(obj=pull_request, path='$.projectKey')
        status = extract_path_value(obj=pull_request, path='$.status.qualityGateStatus')
        analysis_date = extract_path_value(obj=pull_request, path='$.analysisDate')
        try:
            analysis_date = datetime.strptime(analysis_date, '%Y-%m-%dT%H:%M:%S%z')
        except (ValueError, TypeError):
            continue
        if not all([project_key, analysis_date]):
            continue
        project = projects[server_id][project_key]
        project['pull_requests'] += 1
        if analysis_date > recent_window_start:
            project['recent_pr_scans'] += 1
            if status == 'ERROR':
                project['recent_failed_prs'] += 1
    return {server_id: {k for k, v in projects.items() if v['pull_requests'] > 0} for server_id, projects in
            projects.items()}


def process_project_usage(directory, extract_mapping, server_id_mapping, projects):
    for url, project_usage in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                          key='getUsage'):
        server_id = server_id_mapping[url]
        project_key = extract_path_value(obj=project_usage, path='$.projectKey')
        if project_key not in projects[server_id].keys():
            continue
        project = projects[server_id][project_key]
        project['loc'] = extract_path_value(obj=project_usage, path='$.linesOfCode')
        for tier, value in sorted(TIERS.items(), key=lambda x: x[1], reverse=True):
            if project['loc'] >= value and tier != 'unknown':
                project['tier'] = tier
                break
    return projects


def generate_project_metrics_markdown(projects):
    return generate_section(
        headers_mapping={"Server ID": "server_id", "Project Name": "name", "Total Rules": "rules",
                         "Template Rules": "template_rules", "Plugin Rules": "plugin_rules"},
        title='Project Metrics', level=2, filter_lambda=lambda x: True,  # Show all projects for migration report
        rows=[
            project
            for server_id, project_list in projects.items()
            for project in project_list.values()
        ], sort_by_lambda=lambda x: x['rules'],  # Sort by total rules
    )
