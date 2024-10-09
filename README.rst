=================
Sonarqube Reports
=================


Usage
-----
docker run sonar-demos/sonarqube-reports -v ./files:/app/files -e TOKEN="$SONAR_TOKEN" -e URL="$SONAR_URL"

Build from source
-----------------
docker build . -t sonarqube-reports
docker run sonarqube-reports -v ./files:/app/files -e TOKEN="$SONAR_TOKEN" -e URL="$SONAR_URL"