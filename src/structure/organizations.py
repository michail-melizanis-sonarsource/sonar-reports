def map_organization_structure(bindings):
    organizations = list()
    for i in bindings:
        if i['project_count'] < 1:
            continue
        organizations.append(
            dict(
                sonarqube_org_key=i['key'],
                sonarcloud_org_key=None,
                server_url=i['server_url'],
                alm=i['alm'],
                url=i['url'],
                is_cloud=i['is_cloud'],
                project_count=i['project_count'],
            )
        )
    return organizations
