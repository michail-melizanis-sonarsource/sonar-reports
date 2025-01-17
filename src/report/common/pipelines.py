from collections import defaultdict

from utils import multi_extract_object_reader
from datetime import datetime

OVERVIEW_TEMPLATE = """
## CI Environment Overview
| Server ID  | CI Tool | # Projects | First Run | Most Recent Run | Total Scans |
|:-----------|:--------|:------------|-----------|:----------------|:------------|
{pipelines}
"""

DETAILS_TEMPLATE = """
### Project Scan Details
| Server ID | Project Name | CI Tool | # of Scans  | First Scan | Most Recent Scan |
|:----------|:-------------|:--------|:------------|:-----------|:-----------------|
{scan_frequency}
"""


def format_pipelines(extract_directory):
    ci_mapping = dict()
    for analysis in object_reader(directory=extract_directory, key='getProjectAnalyses'):
        if 'detectedCI' not in analysis.keys():
            continue
        if analysis['detectedCI'] not in ci_mapping.keys():
            ci_mapping[analysis['detectedCI']] = dict(projects=set(), scans=0, first_scan=None, last_scan=None)
        ci_mapping[analysis['detectedCI']]['projects'].add(analysis['projectKey'])
        ci_mapping[analysis['detectedCI']]['scans'] += 1
        date = datetime.strptime(analysis['date'], '%Y-%m-%dT%H:%M:%S%z')
        if not ci_mapping[analysis['detectedCI']]['first_scan'] or date < ci_mapping[analysis['detectedCI']][
            'first_scan']:
            ci_mapping[analysis['detectedCI']]['first_scan'] = date
        if not ci_mapping[analysis['detectedCI']]['last_scan'] or date > ci_mapping[analysis['detectedCI']][
            'last_scan']:
            ci_mapping[analysis['detectedCI']]['last_scan'] = date

    return "\n".join([
        "| {name} | {project_count} | {first_scan} | {last_scan} | {total_scans} |".format(
            name=k,
            project_count=len(v['projects']),
            first_scan=v['first_scan'].strftime('%Y-%m-%d'),
            last_scan=v['last_scan'].strftime('%Y-%m-%d'),
            total_scans=v['scans']
        ) for k, v in ci_mapping.items()
    ])


def format_pipeline_overview(project_scans):
    pipelines = [dict(server_id=server_id,
                      name=pipeline,
                      project_count=len(projects),
                      first_scan=min([i['first_scan'] for i in projects.values()]).strftime('%Y-%m-%d'),
                      last_scan=max([i['last_scan'] for i in projects.values()]).strftime('%Y-%m-%d'),
                      total_scans=sum([i['total_scans'] for i in projects.values()])
                      ) for server_id, pipelines in project_scans.items() for pipeline, projects in pipelines.items()]

    return "\n".join(
        [
            "| {server_id} | {name} | {project_count} | {first_scan} | {last_scan} | {total_scans} |".format(**i)
            for i in sorted(pipelines, key=lambda x: x['total_scans'], reverse=True)
        ]
    )


def format_project_scans(project_scans):
    projects = [
        dict(
            server_id=server_id,
            project_name=project_key,
            ci_tool=ci_tool,
            total_scans=scan_data['total_scans'],
            first_scan=scan_data['first_scan'].strftime('%Y-%m-%d'),
            last_scan=scan_data['last_scan'].strftime('%Y-%m-%d')
        )
        for server_id, pipelines in project_scans.items()
        for ci_tool, projects in pipelines.items()
        for project_key, scan_data in projects.items()
    ]

    return "\n".join(
        [
            "| {server_id} | {project_name} | {ci_tool} | {total_scans} | {first_scan} | {last_scan} |".format(**i)
            for i in sorted(projects, key=lambda x: x['total_scans'], reverse=True)
        ]
    )


def process_scan_details(directory, extract_mapping, server_id_mapping):
    project_scans = defaultdict(dict)
    for url, analysis in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                     key='getProjectAnalyses'):
        server_id = server_id_mapping[url]
        date = datetime.strptime(analysis['date'], '%Y-%m-%dT%H:%M:%S%z')
        if 'detectedCI' not in analysis.keys():
            continue
        if analysis['detectedCI'] not in project_scans[server_id].keys():
            project_scans[server_id][analysis['detectedCI']] = dict()
        if analysis['projectKey'] not in project_scans[server_id][analysis['detectedCI']].keys():
            project_scans[server_id][analysis['detectedCI']][analysis['projectKey']] = dict(
                total_scans=0,
                first_scan=None,
                last_scan=None
            )
        project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['total_scans'] += 1
        first_scan = project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['first_scan']
        last_scan = project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['last_scan']
        if not first_scan or date < first_scan:
            first_scan = date
        if not last_scan or date > last_scan:
            last_scan = date
        project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['first_scan'] = first_scan
        project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['last_scan'] = last_scan
    return project_scans


def generate_pipeline_markdown(directory, extract_mapping, server_id_mapping):
    project_scans = process_scan_details(
        directory=directory,
        extract_mapping=extract_mapping,
        server_id_mapping=server_id_mapping
    )
    overview = OVERVIEW_TEMPLATE.format(
        pipelines=format_pipeline_overview(project_scans=project_scans)
    )
    details = DETAILS_TEMPLATE.format(
        scan_frequency=format_project_scans(project_scans=project_scans)
    )
    return overview, details
