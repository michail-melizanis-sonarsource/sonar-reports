import csv
import json
from datetime import datetime, UTC
from email.policy import default

from constants import REPORT_TASKS, MIGRATION_TASKS
import click
import os
from execute import execute_plan
from logs import configure_logger
from operations.http_request import configure_client, configure_client_cert, get_server_details
from plan import generate_task_plan, get_available_task_configs
from utils import get_latest_extract_id, get_unique_extracts, export_csv, load_csv
from validate import validate_migration

@click.group()
def cli():
    pass


@cli.command()
@click.argument('url')
@click.argument('token')
@click.option('--pem_file_path')
@click.option('--key_file_path')
@click.option('--cert_password')
@click.option('--export_directory', default='/app/files/')
@click.option('--extract_type', default='all', help='Type of Extract to run')
@click.option('--concurrency', default=25)
@click.option('--timeout', default=60)
@click.option('--extract_id', default=None)
def extract(url, token, export_directory: str, extract_type, pem_file_path=None, key_file_path=None, cert_password=None,
            concurrency=25,
            timeout=60, extract_id=None, ):
    if not url.endswith('/'):
        url = f"{url}/"
    if extract_id is None:
        extract_id = str(int(datetime.now(UTC).timestamp()))
    cert = configure_client_cert(key_file_path, pem_file_path, cert_password)
    server_version, edition = get_server_details(url=url, cert=cert, token=token)
    extract_directory = os.path.join(export_directory, extract_id + '/')
    os.makedirs(extract_directory, exist_ok=True)
    configure_logger(name='http_request', level='INFO', output_file=os.path.join(extract_directory, 'requests.log'))
    configure_client(url=url, cert=cert, server_version=server_version, token=token, concurrency=concurrency,
                     timeout=timeout)
    configs = get_available_task_configs(client_version=server_version, edition=edition)
    if extract_type == 'report':
        target_tasks = REPORT_TASKS
    elif extract_type == 'migration':
        target_tasks = MIGRATION_TASKS
    else:
        target_tasks = list([k for k in configs.keys() if k.startswith('get')])
    plan = generate_task_plan(target_tasks=target_tasks, task_configs=configs)
    with open(os.path.join(extract_directory, 'plan.json'), 'wt') as f:
        json.dump(
            dict(
                plan=plan,
                version=server_version,
                edition=edition,
                url=url,
                target_tasks=target_tasks,
                available_configs=list(configs.keys()),
                extract_id=extract_id,
            ), f
        )
    execute_plan(execution_plan=plan, inputs=dict(url=url), concurrency=concurrency, task_configs=configs,
                 output_directory=export_directory, current_run_id=extract_id, run_ids={extract_id})
    click.echo(f"Extract Complete: {extract_id}")


@cli.command()
@click.option('--export_directory', default='/app/files/')
@click.option('--extract_id', default=None)
def report(export_directory, extract_id):
    from report.generate import generate_markdown
    if extract_id is None:
        extract_id = get_latest_extract_id(export_directory)
    else:
        extract_id = extract_id.strip()
    if extract_id is None or not os.path.isdir(os.path.join(export_directory, extract_id)):
        click.echo("No Extracts Found")
        return
    generate_markdown(extract_directory=os.path.join(export_directory, extract_id.strip() + '/'))


@cli.command()
@click.option('--export_directory', default='/app/files/')
def structure(export_directory):
    from structure import map_organization_structure, map_project_structure
    extract_mapping = get_unique_extracts(directory=export_directory)
    bindings, projects = map_project_structure(export_directory=export_directory, extract_mapping=extract_mapping)
    organizations = map_organization_structure(bindings)
    export_csv(directory=export_directory, name='organizations', data=organizations)
    export_csv(directory=export_directory, name='projects', data=projects)


@cli.command()
@click.option('--export_directory', default='/app/files/')
def mappings(export_directory):
    from structure import map_templates, map_groups, map_profiles, map_gates, map_portfolios
    extract_mapping = get_unique_extracts(directory=export_directory)
    projects = load_csv(directory=export_directory, filename='projects.csv')
    project_org_mapping = {p['server_url'] + p['key']: p['sonarqube_org_key'] for p in projects}
    mapping = dict(
        templates=map_templates(project_org_mapping=project_org_mapping, extract_mapping=extract_mapping,
                                export_directory=export_directory),
        profiles=map_profiles(extract_mapping=extract_mapping, project_org_mapping=project_org_mapping,
                              export_directory=export_directory),
        gates=map_gates(project_org_mapping=project_org_mapping, extract_mapping=extract_mapping,
                        export_directory=export_directory),
        portfolios = map_portfolios(export_directory=export_directory, extract_mapping=extract_mapping)
    )
    mapping['groups'] = map_groups(project_org_mapping=project_org_mapping, profiles=mapping['profiles'],
                                   extract_mapping=extract_mapping, export_directory=export_directory, templates=mapping['templates'])
    for k, v in mapping.items():
        export_csv(directory=export_directory, name=k, data=v)


@cli.command()
@click.argument('token')
@click.option('--edition', default='enterprise')
@click.option('--url', default='https://sonarcloud.io/')
@click.option('--run_id', default=None)
@click.option('--concurrency', default=25)
@click.option('--export_directory', default='/app/files/')
def migrate(token, edition, url, concurrency, run_id, export_directory):
    configure_client(url=url, cert=None, server_version="cloud", token=token)
    if run_id is None:
        run_id = str(int(datetime.now(UTC).timestamp()))
    run_dir, completed = validate_migration(directory=export_directory, run_id=run_id)
    extract_mapping = get_unique_extracts(directory=export_directory)
    configure_logger(name='http_request', level='INFO', output_file=os.path.join(run_dir, 'requests.log'))
    configs = get_available_task_configs(client_version='cloud', edition=edition)
    plan = generate_task_plan(
        target_tasks=list([k for k, v in configs.keys() if not k.startswith('get')]),
        task_configs=configs, completed=completed)
    execute_plan(execution_plan=plan, inputs=dict(url=url), concurrency=concurrency, task_configs=configs,
                 output_directory=export_directory, current_run_id=run_id, run_ids=set(extract_mapping.values()).union({run_id}))


if __name__ == '__main__':
    cli()
