from collections import defaultdict

from report.utils import generate_section
from utils import multi_extract_object_reader
from datetime import datetime, timedelta, UTC


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
                last_scan=None,
                scan_count_30_days=0,
                failed_scans=0,
                failed_scans_30_days=0
            )
        failed = False
        for event in analysis.get('events', []):
            if event['category'] == 'QUALITY_GATE':
                if event['name'].upper() == 'FAILED':
                    failed=True
                    project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['failed_scans'] += 1
                break
        project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['total_scans'] += 1
        first_scan = project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['first_scan']
        last_scan = project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['last_scan']
        if date> datetime.now(tz=UTC) - timedelta(days=30):
            project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['scan_count_30_days'] += 1
            if failed:
                project_scans[server_id][analysis['detectedCI']][analysis['projectKey']]['failed_scans_30_days'] += 1
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
    overview = generate_section(
        headers_mapping={
            "Server ID": "server_id",
            "CI Tool": "name",
            "# Projects": "project_count",
            "First Run": "first_scan",
            "Most Recent Run": "last_scan",
            "Total Scans": "total_scans"
        },
        level=2,
        rows=[
            dict(server_id=server_id,
                 name=pipeline,
                 project_count=len(projects),
                 first_scan=min([i['first_scan'] for i in projects.values()]).strftime('%Y-%m-%d'),
                 last_scan=max([i['last_scan'] for i in projects.values()]).strftime('%Y-%m-%d'),
                 total_scans=sum([i['total_scans'] for i in projects.values()])
                 ) for server_id, pipelines in project_scans.items() for pipeline, projects in pipelines.items()],
        title="CI Environment Overview",
        sort_by_lambda=lambda x: x['total_scans'],
        sort_order='desc'
    )
    details = generate_section(
        headers_mapping={
            "Server ID": "server_id",
            "Project Name": "project_name",
            "CI Tool": "ci_tool",
            "# of Scans": "total_scans",
            "First Scan": "first_scan",
            "Most Recent Scan": "last_scan"
        },
        level=3,
        rows=[dict(
            server_id=server_id,
            project_name=project_key,
            ci_tool=ci_tool,
            total_scans=scan_data['total_scans'],
            first_scan=scan_data['first_scan'].strftime('%Y-%m-%d'),
            last_scan=scan_data['last_scan'].strftime('%Y-%m-%d')
        )
            for server_id, pipelines in project_scans.items()
            for ci_tool, projects in pipelines.items()
            for project_key, scan_data in projects.items()],
        title="Project Scan Details",
        sort_by_lambda=lambda x: x['total_scans'],
        sort_order='desc'
    )
    return overview, details, project_scans
