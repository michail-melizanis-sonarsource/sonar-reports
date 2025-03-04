import asyncio
from collections import defaultdict
import os
import itertools
from functools import partial
from parser import set_path_value, extract_path_value
from pipelines.utils import load_module
from utils import object_reader
from asyncio import gather
from pipelines.platforms import get_platform_module
from pipelines.pipelines import identify_pipeline_type
from ruamel.yaml import YAML
from io import StringIO

CLOUD_TOKEN_NAME = 'SONARQUBE_CLOUD_TOKEN'
CLOUD_URL_NAME = 'SONARQUBE_CLOUD_URL'


async def update_pipelines(migration_directory, org_secret_mapping, sonar_token, sonar_url):
    orgs, secrets = await create_org_secrets(
        migration_directory=migration_directory,
        org_secret_mapping=org_secret_mapping,
        sonar_token=sonar_token, sonar_url=sonar_url
    )
    await update_repos(organization_mapping=orgs, migration_directory=migration_directory)


async def create_org_secrets(migration_directory, org_secret_mapping, sonar_token, sonar_url):
    global CLOUD_TOKEN_NAME, CLOUD_URL_NAME
    secrets_updates = []
    secrets = [
        dict(
            secret_name=CLOUD_TOKEN_NAME,
            secret_value=sonar_token
        ),
        dict(
            secret_name=CLOUD_URL_NAME,
            secret_value=sonar_url
        )
    ]
    organizations = dict()
    for organization in object_reader(migration_directory, 'generateOrganizationMappings'):
        if not organization.get('is_cloud', False):
            continue
        organization['token'] = org_secret_mapping[organization['sonarqube_org_key']]
        organizations[organization['sonarcloud_org_key']] = organization
        if organization.get('alm') == 'azure':
            continue
        platform = get_platform_module(name=organization['alm'])
        for secret in secrets:
            secrets_updates.append(
                platform.create_org_secret(
                    organization=organization,
                    token=org_secret_mapping[organization['sonarqube_org_key']],
                    **secret
                )
            )
    return organizations, await gather(*secrets_updates)


async def update_repos(organization_mapping, migration_directory):
    repos = defaultdict(lambda: dict(projects=dict(), organization=dict(), repository=None))
    pull_requests = dict()
    for project in object_reader(migration_directory, 'createProjects'):
        if project['sonarCloudOrgKey'] in organization_mapping and project['repository']:
            repos[project['repository']]['repository'] = project['repository']
            repos[project['repository']]['projects'][project['sourceProjectKey']] = project,
            repos[project['repository']]['organization'] = organization_mapping[project['sonarCloudOrgKey']]
    for repo in repos.values():
        pull_request = await update_repository(token=repo['organization']['token'], projects=repo['projects'],
                                               organization=repo['organization'], repo_string=repo['repository'])
        if pull_request:
            pull_requests[repo['repository']] = pull_request
    return pull_requests


async def update_repository(token, repo_string, projects, organization):
    platform = get_platform_module(name=organization['alm'])
    repository = platform.generate_repository_string(repo_string=repo_string, organization=organization)
    default_branch = await platform.get_default_branch(token=token, repository=repository)
    pipeline_files = await platform.get_pipeline_files(token=token, repository=repository, branch=default_branch)
    branch = await platform.create_branch(token=token, repository=repository,
                                          branch_name='sonar/auto-migrate-pipelines',
                                          base_branch_name=default_branch)
    updated_files = await update_pipeline_files(
        repository=repository,
        files=pipeline_files,
        token=token,
        branch_name=branch['name'],
        platform=platform,
        projects=projects,
    )
    pr = None
    if updated_files:
        pr = await platform.create_pull_request(
            token=token,
            repository=repository,
            source_branch=branch['name'],
            target_branch=default_branch,
            title='Auto migrate pipelines',
            body='Auto migrate pipelines',
        )
    return pr


async def update_pipeline_files(platform, projects, repository, branch_name, files, token):
    loop = asyncio.get_event_loop()
    updates = list()
    updated_files = list()
    for file, _ in files:
        file['yaml'] = YAML().load(file['content'])
        updates.append(
            loop.run_in_executor(
                None,
                partial(
                    update_pipeline_file,
                    platform=platform,
                    file=file,
                ), ()
            )
        )
    updated = await gather(*updates)
    mappings = defaultdict(lambda: dict(projects=set(), scanners=set()))
    for file, dir_project_mapping in updated:
        if file['is_updated']:
            updated_files.append(file)
        for key, value in dir_project_mapping.items():
            mappings[key]['projects'] = mappings[key]['projects'].union(value['projects'])
            mappings[key]['scanners'] = mappings[key]['scanners'].union(value['scanners'])

    updated_configs = await gather(*[update_config_file(
        platform=platform,
        project_mappings=projects,
        repository=repository,
        branch_name=branch_name,
        root_dir=root_dir,
        projects=mapped['projects'],
        scanners=mapped['scanners'],
        token=token
    ) for root_dir, mapped in mappings.items()])
    updated_files += [i for i in itertools.chain.from_iterable(updated_configs) if i['is_updated']]
    await gather(*[
        platform.create_or_update_file(
            token=token,
            repository=repository,
            branch_name=branch_name,
            file_path=i['file_path'],
            content=i['updated_content'],
            sha=i['sha']
        ) for i in updated_files
    ])
    return updated_files

def update_pipeline_file(platform, file):
    pipeline_type = identify_pipeline_type(platform=platform, file=file)
    targets = pipeline_type.process_yaml(file=file)
    dir_project_mapping = dict()
    is_updated = False
    for target in targets:
        file['yaml'], dir_project_mapping = update_pipeline_target(
            pipeline_type=pipeline_type,
            yaml=file['yaml'],
            target=target,
            dir_project_mapping=dir_project_mapping
        )
        is_updated = True
    if is_updated:
        with StringIO() as output:
            YAML().dump(file['yaml'], output)
            output.seek(0)
            file['updated_content'] = output.read()
            file['is_updated'] = True
    return file, dir_project_mapping


async def update_config_file(platform, project_mappings, projects, root_dir, scanners, repository, branch_name, token):
    if not scanners:
        scanners = {'cli'}
    content = list()
    if not projects:
        projects = set(list(project_mappings.keys())[0])
    for scanner in scanners:
        mod = load_module(mod_type='scanners', name=scanner)
        file_names = mod.get_config_file_name()
        for file_name in file_names:
            file_path = os.path.join(root_dir, file_name)
            content.append(
                platform.get_content(
                    token=token,
                    repository=repository,
                    file_path=file_path,
                    branch=branch_name,
                    extra_args=dict(file_name=file_path, scanner_mod=mod, scanner=scanner)
                )
            )
    content = await gather(*content)
    updated_configs = [
        dict(
            **extra['scanner_mod'].update_content(
                content=file['content'],
                projects=projects,
                project_mappings=project_mappings,
            ), **file
        )
        for file, extra in content if file['content'] or extra['scanner'] == 'cli'
    ]
    return updated_configs


def update_pipeline_variables(pipeline_type, yaml, variables):
    for env, path in variables.items():
        if env == 'SONAR_TOKEN':
            yaml = set_path_value(obj=yaml, path=path,
                                  val=pipeline_type.format_variable(value=CLOUD_TOKEN_NAME, var_type='secret'))
        elif env == 'SONAR_HOST_URL':
            yaml = set_path_value(obj=yaml, path=path,
                                  val=pipeline_type.format_variable(value=CLOUD_URL_NAME, var_type='secret'))
    return yaml


def update_pipeline_target(pipeline_type, yaml, target, dir_project_mapping):
    yaml = update_pipeline_variables(pipeline_type=pipeline_type, yaml=yaml, variables=target['variables'])
    for task in target['tasks']:
        yaml = update_pipeline_variables(pipeline_type=pipeline_type, yaml=yaml, variables=task['variables'])
        if task['script']:
            script = extract_path_value(obj=yaml, path=task['script'], default='')
            updated, dir_project_mapping = update_script(
                script=script,
                root_dir=task['working_dir'],
                dir_project_mapping=dir_project_mapping
            )
            set_path_value(obj=yaml, path=task['script'], val=updated)
    return yaml, dir_project_mapping


def update_script(script, root_dir, dir_project_mapping):
    from pipelines.runtimes.unix import update_script as unix_update_script
    updated, dir_project_mapping = unix_update_script(script=script, root_dir=root_dir,
                                                      dir_project_mapping=dir_project_mapping)
    return updated, dir_project_mapping
