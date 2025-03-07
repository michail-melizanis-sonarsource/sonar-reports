def get_mappings():
    return {
        "sonar.projectKey": "$.key",
        "sonar.projectName": "$.name",
        "sonar.organization": "$.sonarCloudOrgKey"
    }