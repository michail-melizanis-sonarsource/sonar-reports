from utils import multi_extract_object_reader


def flatten_dependencies(profile_map, profile_key):
    dependencies = {profile_key}
    profile = profile_map[profile_key]
    if profile.get('parentKey'):
        parent_key = profile['parentKey']
        dependencies.update(flatten_dependencies(profile_map, parent_key))
    return dependencies


def add_profile(profile_map, results, org_key, server_url, profile_key):
    if profile_key in profile_map.keys() and not profile_map[profile_key].get('isBuiltIn'):
        profile = profile_map[profile_key]
        unique_key = org_key + profile_key
        results[unique_key] = dict(
            unique_key=unique_key,
            name=profile['name'],
            language=profile['language'],
            parent_name=profile_map.get(profile.get('parentKey'), dict()).get('name'),
            server_url=server_url,
            is_default=profile_map[profile_key].get('isDefault', False),
            source_profile_key=profile_key,
            sonarqube_org_key=org_key,
        )
        if profile.get('parentKey'):
            results = add_profile(profile_map=profile_map, results=results, org_key=org_key, server_url=server_url,
                                  profile_key=profile['parentKey'])
    return results


def map_profiles(project_org_mapping, extract_mapping, export_directory):
    results = dict()
    profiles = {
        profile['key']: profile for server_url, profile in
        multi_extract_object_reader(directory=export_directory, mapping=extract_mapping, key='getProfiles')
    }
    for server_url, project_details in multi_extract_object_reader(directory=export_directory, mapping=extract_mapping,
                                                                   key='getProjectDetails'):
        if server_url + project_details['projectKey'] not in project_org_mapping.keys():
            continue
        org_key = project_org_mapping[server_url + project_details['projectKey']]
        for profile in project_details.get('qualityProfiles', []):
            if profile.get('deleted', False):
                continue
            profile_key = profile['key']
            results = add_profile(profile_map=profiles, results=results, org_key=org_key, server_url=server_url,
                                  profile_key=profile_key)
    for org_key in set(project_org_mapping.values()):
        for profile in profiles.values():
            if not profile['isDefault']:
                continue
            results = add_profile(profile_map=profiles, results=results, org_key=org_key,
                                  server_url=profile['serverUrl'],
                                  profile_key=profile['key'])
    return list(results.values())
