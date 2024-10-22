from .extract import execute_extraction_plan
from .plan import generate_extraction_plan, get_available_entity_configs
from asyncio import get_event_loop
import os
import json
from shutil import rmtree
from .utils import get_server_details, configure_client_cert
from datetime import datetime
from logs import configure_logger

def generate_extract_plan(export_directory, cert, token, url, timeout, entities):
    plan_file_path = os.path.join(export_directory, 'extraction_plan.json')
    extraction_plan, server_version, edition = None, None, None
    if os.path.exists(plan_file_path):
        with open(plan_file_path, 'rt') as f:
            extraction_details = json.load(f)
            extraction_plan = extraction_details['extraction_plan']
            server_version = extraction_details['server_version']
            edition = extraction_details['edition']
            entities = extraction_details['entity_types']
    if server_version is None:
        server_version, edition = get_server_details(url=url, cert=cert, token=token, timeout=timeout)
    configs = get_available_entity_configs(server_version=server_version, edition=edition)

    if extraction_plan is None:
        extraction_plan = generate_extraction_plan(
            entities=entities if entities is not None else list(configs.keys()),
            entity_configs=configs
        )
        with open(plan_file_path, 'wt') as f:
            json.dump(dict(
                entity_types=list(configs.keys()),
                server_version=server_version,
                edition=edition,
                extraction_plan=extraction_plan
            ), f)
    extraction_plan = filter_completed_stages(extraction_plan=extraction_plan, export_directory=export_directory)
    return extraction_plan, server_version, edition, configs


def filter_completed_stages(extraction_plan, export_directory):
    filtered_plan = list()
    last_completed = None
    for phase in extraction_plan:
        filtered_phase = list()
        for stage in phase:
            completed = False
            if os.path.exists(os.path.join(export_directory, stage)):
                completed = True
                last_completed = stage
            if not completed:
                filtered_phase.append(stage)
        if len(filtered_phase) > 0:
            filtered_plan.append(filtered_phase)
    if len(filtered_plan) == 0:
        filtered_plan.append([])
    if last_completed is not None:
        rmtree(os.path.join(export_directory, last_completed), ignore_errors=True)
        filtered_plan[0] = [last_completed] + filtered_plan[0]
    return filtered_plan


def run_extract(token, url, key_file_path, pem_file_path, cert_password, max_threads, export_directory, timeout, extract_id=None,
                entities=None):
    cert = configure_client_cert(key_file_path, pem_file_path, cert_password)
    if extract_id is None:
        extract_id = int(datetime.utcnow().timestamp())

    extract_directory = os.path.join(export_directory, str(extract_id))
    os.makedirs(extract_directory, exist_ok=True)
    configure_logger(name='default', level='WARNING')
    configure_logger(name='extract', level='INFO', output_file=os.path.join(extract_directory, 'errors.log'))

    extraction_plan, server_version, edition, configs = generate_extract_plan(
        export_directory=extract_directory,
        cert=cert,
        token=token,
        url=url,
        timeout=timeout,
        entities=entities
    )
    loop = get_event_loop()
    loop.run_until_complete(
        execute_extraction_plan(
            cert=cert,
            timeout=timeout,
            server_version=server_version,
            entity_configs=configs,
            extraction_plan=extraction_plan,
            directory=extract_directory,
            max_threads=max_threads,
            token=token,
            base_url=url
        )
    )
    return extract_id, extract_directory
