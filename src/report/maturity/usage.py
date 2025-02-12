from collections import defaultdict

from report.common.projects import TIERS


def generate_usage_markdown(projects, scans):
    from report.utils import generate_section
    active_projects = defaultdict(dict)
    for server, cis in scans.items():
        for ci, projects_scanned in cis.items():
            for key, project in projects_scanned.items():
                if key not in projects[server].keys():
                    continue
                if project['scan_count_30_days'] > 0:
                    active_projects[projects[server][key]['tier']][key] = projects[server][key].get('loc', 0)
                if '30_day_scans' not in projects[server][key]:
                    projects[server][key]['30_day_scans'] = 0
                projects[server][key]['30_day_scans'] += project['scan_count_30_days']
    rows = {
        key: dict(
            size=f"{key.upper()} > {val:,} LOC",
            scans_per_day=0,
            projects=0,
            active_projects=len(active_projects[key]),
            scanned_code=sum(active_projects[key].values())
        ) for key, val in TIERS.items()
    }
    for server_projects in projects.values():
        for project in server_projects.values():
            rows[project['tier']]['projects'] += 1
            rows[project['tier']]['scans_per_day'] += project.get('30_day_scans', 0) / 30

    return generate_section(
        headers_mapping={
            "Size": "size",
            "Projects": "projects",
            "Scans Per Day": "scans_per_day",
            "Projects Scanned (30 Days)": "active_projects",
            "Active Scanned Code": "scanned_code",
        },
        level=3,
        rows=rows.values(),
        title="Usage"
    )
