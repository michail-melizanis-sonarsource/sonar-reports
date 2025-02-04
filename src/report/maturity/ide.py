from report.utils import generate_section
from datetime import datetime, timedelta, UTC

def generate_ide_markdown(users):
    row = dict(
        total = 0,
        active=0
    )
    for server_users in users.values():
        for user in server_users:
            connection = user.get('sonarLintLastConnectionDate')
            if connection:
                row['total'] += 1
                if datetime.strptime(connection, '%Y-%m-%dT%H:%M:%S%z') > datetime.now(tz=UTC) - timedelta(days=30):
                    row['active'] += 1
    return generate_section(
        title="IDE Integration",
        headers_mapping={
            "Connected Mode Users": "total",
            "Active Connected Mode Users": "active"
        },
        rows=[row]
    )
