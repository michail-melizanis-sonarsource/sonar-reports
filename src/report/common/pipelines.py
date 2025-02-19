from collections import defaultdict

from parser import extract_path_value
from report.utils import generate_section
from utils import multi_extract_object_reader
from datetime import datetime, timedelta, UTC


def process_scan_details(directory, extract_mapping, server_id_mapping):
    project_scans = defaultdict(lambda: defaultdict(lambda : defaultdict(lambda : dict(
        project_key=None,
        server_id=None,
        total_scans=0,
        first_scan=None,
        last_scan=None,
        scan_count_30_days=0,
        failed_scans=0,
        failed_scans_30_days=0
    ))))
    for url, analysis in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                     key='getProjectAnalyses'):
        server_id = server_id_mapping[url]
        scan_date = extract_path_value(obj=analysis, path='$.date')
        detected_ci = extract_path_value(obj=analysis, path='$.detectedCI')
        project_key = extract_path_value(obj=analysis, path='$.projectKey')
        if not all([scan_date, detected_ci, project_key]):
            continue
        date = datetime.strptime(scan_date, '%Y-%m-%dT%H:%M:%S%z')
        project_scans[server_id][detected_ci][project_key].update(
            dict(
                project_key=project_key,
                server_id=server_id
            )
        )
        failed = False
        scan = project_scans[server_id][detected_ci][project_key]
        for event in extract_path_value(obj=analysis, path='events', default=list()):
            category = extract_path_value(obj=event, path='category')
            status = extract_path_value(obj=event, path='name')
            if category == 'QUALITY_GATE' and status == 'FAILED':
                failed = True
                scan['failed_scans'] += 1
                break
        scan['total_scans'] += 1
        first_scan = scan['first_scan']
        last_scan = scan['last_scan']
        if date> datetime.now(tz=UTC) - timedelta(days=30):
            scan['scan_count_30_days'] += 1
            if failed:
                scan['failed_scans_30_days'] += 1
        if not first_scan or date < first_scan:
            first_scan = date
        if not last_scan or date > last_scan:
            last_scan = date
        scan['first_scan'] = first_scan
        scan['last_scan'] = last_scan
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
                 first_scan=min([i['first_scan'] for i in projects.values()]),
                 last_scan=max([i['last_scan'] for i in projects.values()]),
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
            first_scan=scan_data['first_scan'],
            last_scan=scan_data['last_scan']
        )
            for server_id, pipelines in project_scans.items()
            for ci_tool, projects in pipelines.items()
            for project_key, scan_data in projects.items()],
        title="Project Scan Details",
        sort_by_lambda=lambda x: x['total_scans'],
        sort_order='desc'
    )
    return overview, details, project_scans
