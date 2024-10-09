#!bin/bash
sonar-migration -u "$URL" -t "$TOKEN" -f /app/files/export.json
python /app/cli.py /app/files/export.json /app/files/report.md
