from datetime import datetime, UTC
from constants import REPORT_TASKS, MIGRATION_TASKS
import click
import os
from execute import execute_plan
from logs import configure_logger
from operations.http_request import configure_client, configure_client_cert, get_server_details
from plan import generate_task_plan, get_available_task_configs


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
@click.option('--extract_type', default='report', help='Type of Extract to run')
@click.option('--concurrency', default=25)
@click.option('--timeout', default=60)
@click.option('--extract_id', default=None)
def extract(url, token, export_directory:str, pem_file_path=None, key_file_path=None, cert_password=None, concurrency=25,
            timeout=60, extract_id=None, extract_type='report'):
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
    execute_plan(execution_plan=plan, inputs=dict(url=url), concurrency=concurrency, task_configs=configs,
                 output_directory=extract_directory)
    print(extract_id)

# @cli.command()
# @click.argument('url')
# @click.option('--export_directory')
# @click.option('--extract_id', default=None)
def report(url, export_directory='/app/files/', extract_id=None):
    from report.generate import generate_markdown
    generate_markdown(url=url, extract_directory=os.path.join(export_directory, extract_id.strip() + '/'))


@cli.command()
@click.argument('url')
@click.option('--export_directory')
def structure(url, export_directory='/app/files/'):
    from structure.organizations import generate_org_structure
    generate_org_structure(export_directory=export_directory)


@cli.command()
@click.argument('token')
@click.option('--edition')
@click.option('--url')
def migrate(token, edition='enterprise', url='https://sonarcloud.io/', max_threads=25, export_directory='/app/files/'):
    configure_client(url=url, cert=None, server_version="cloud", token=token)
    configs = get_available_task_configs(client_version='cloud', edition=edition)
    plan = generate_task_plan(
        target_tasks=list([k for k, v in configs.keys() if not k.startswith('get')]),
        task_configs=configs)
    execute_plan(execution_plan=plan, inputs=dict(url=url), concurrency=max_threads, task_configs=configs,
                 output_directory=export_directory)


if __name__ == '__main__':
    cli()
