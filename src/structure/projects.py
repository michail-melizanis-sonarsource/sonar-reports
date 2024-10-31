from utils import multi_extract_object_reader


def is_cloud_binding(binding):
    is_cloud = False
    cloud_endpoints = ['dev.azure.com', 'gitlab.com', 'api.github.com', 'bitbucket.org']
    if any([endpoint in binding.get('url', '') for endpoint in cloud_endpoints]):
        is_cloud = True
    return is_cloud


def generate_unique_project_key(server_url, key, alm=None, repository=None, monorepo=False):
    if repository and alm and not monorepo:
        return f"{alm}_{repository}"
    else:
        return server_url + key


def generate_unique_binding_key(server_url, key, alm, url, repository):
    if alm is None or url is None:
        return server_url
    base_url = url.replace('https://', '').replace('http://', '').split('/')[0]
    if alm in ['gitlab']:
        org_key = f"{key} - {server_url}"
    elif alm in ['github']:
        org_key = repository.split("/")[0]
    else:
        url = url.strip('/')
        org_key = url.split("/")[-1]
    return base_url + '/' + org_key


def map_project_structure(export_directory, extract_mapping):
    projects = dict()
    binding_mapping = {server_url + binding['key']: binding for server_url, binding in
                       multi_extract_object_reader(directory=export_directory, key='getBindings',
                                                   mapping=extract_mapping)}
    unique_bindings = dict()
    project_bindings = {
        server_url + project_binding['projectKey']: dict(
            binding=binding_mapping.get(server_url + project_binding['key']), project_binding=project_binding) for
        server_url, project_binding in
        multi_extract_object_reader(directory=export_directory, key='getProjectBindings', mapping=extract_mapping)
    }
    for server_url, project in multi_extract_object_reader(directory=export_directory, key='getProjects',
                                                           mapping=extract_mapping):
        project_binding = project_bindings.get(server_url + project['key'], dict(binding=dict(key=server_url)))
        unique_binding_key = generate_unique_binding_key(
            server_url=server_url,
            key=project_binding['binding']['key'],
            alm=project_binding['binding'].get('alm'),
            url=project_binding['binding'].get('url'),
            repository=project_binding.get('project_binding', dict()).get('repository')
        )
        if unique_binding_key not in unique_bindings.keys():
            unique_bindings[unique_binding_key] = dict(
                key=unique_binding_key,
                alm=project_binding['binding'].get('alm'),
                url=project_binding['binding'].get('url'),
                server_url=server_url,
                is_cloud=is_cloud_binding(binding=project_binding['binding']),
                project_count=0,
            )
        unique_bindings[unique_binding_key]['project_count'] += 1
        unique_project_key = generate_unique_project_key(
            server_url=server_url,
            key=project['key'],
            alm=project_binding['binding'].get('alm'),
            repository=project_binding.get('project_binding', dict()).get('repository'),
            monorepo=project_binding.get('project_binding', dict()).get('monorepo', False),
        )
        projects[unique_project_key] = dict(
            key=project['key'],
            name=project['name'],
            server_url=server_url,
            sonarqube_org_key=unique_binding_key,
            is_cloud_binding=is_cloud_binding(binding=project_binding['binding']),
            repository=project_binding.get('project_binding', dict()).get('repository'),
            monorepo=project_binding.get('project_binding', dict()).get('monorepo', False),
            summary_comment_enabled=project_binding.get('project_binding', dict()).get('summaryCommentEnabled', False),
        )
        # TODO add main branch
        # todo add new code definition
        # add gate
        # add profiles
    return list(unique_bindings.values()), list(projects.values())
