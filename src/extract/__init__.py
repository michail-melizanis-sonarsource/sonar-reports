from .extract import execute_extraction_plan
from .plan import generate_extraction_plan, get_available_entity_configs
from asyncio import get_event_loop
import os
import json

from .utils import get_server_details, configure_client_cert


def run_extract(token, url, key_file_path, pem_file_path, cert_password, max_threads, export_directory, timeout,
                entities=None):
    cert = configure_client_cert(key_file_path, pem_file_path, cert_password)
    server_version, edition = get_server_details(url=url, cert=cert, token=token, timeout=timeout)
    configs = get_available_entity_configs(server_version=server_version, edition=edition)

    extraction_plan = generate_extraction_plan(
        entities=entities if entities is not None else list(configs.keys()),
        entity_configs=configs
    )
    with open(os.path.join(export_directory, 'extraction_plan.json'), 'wt') as f:
        json.dump(dict(
            entity_types=list(configs.keys()),
            server_version=server_version,
            edition=edition,
            extraction_plan=extraction_plan
        ), f)

    loop = get_event_loop()
    loop.run_until_complete(
        execute_extraction_plan(
            cert=cert,
            timeout=timeout,
            server_version=server_version,
            entity_configs=configs,
            extraction_plan=extraction_plan,
            directory=export_directory,
            max_threads=max_threads,
            token=token,
            base_url=url
        )
    )
    return export_directory
