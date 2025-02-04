from report.utils import generate_section


def generate_scans_markdown(project_scans):
    scans = [project for server_ci in project_scans.values() for ci_projects in server_ci.values() for project in
             ci_projects.values()]
    row = dict(
        projects_scanned_30_days=sum([i['scan_count_30_days'] for i in scans]),
        failed_scans_30_days=sum([i['failed_scans_30_days'] for i in scans]),
        projects_with_failed_scans_30_days=len(
            [i for i in scans if i['failed_scans_30_days'] > 0])
    )
    return generate_section(
        title='Scans',
        headers_mapping={
            "Projects Scanned (Past 30 Days)": "projects_scanned_30_days",
            "Failed Scans (Past 30 Days)": "failed_scans_30_days",
            "Projects with failed Scans (Past 30 Days)": "projects_with_failed_scans_30_days",
        },
        rows=[row]
    )
