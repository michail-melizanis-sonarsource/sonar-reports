=================
Sonarqube Reports
=================


Usage
-----
docker run -v ./files:/app/files -e TOKEN="$SONAR_TOKEN" -e URL="$SONAR_URL" sonar-demos/sonarqube-reports

Build from source
-----------------
docker build . -t sonarqube-reports
docker run -v ./files:/app/files -e TOKEN="$SONAR_TOKEN" -e URL="$SONAR_URL" sonarqube-reports