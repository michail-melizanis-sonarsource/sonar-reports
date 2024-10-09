#!bin/bash
sonar-migration -u "$URL" -t "$TOKEN" -f /app/files/export.json
python /app/cli.py /app/files/peach.16.issues.json /app/files/report.md
