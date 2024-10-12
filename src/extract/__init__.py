from platform import version

from .extract import execute_extraction_plan
from .plan import generate_extraction_plan, get_available_entity_configs
from asyncio import get_event_loop
from httpx import Client
import os
import json





def run_extract(token, url, key_file_path, pem_file_path, cert_password, max_threads, export_directory, entities=None):
    cert = tuple([i for i in [pem_file_path, key_file_path, cert_password] if i is not None])
    sync_client = Client(base_url=url, cert=cert if cert else None)
    server_version_resp = sync_client.get("/api/server/version", headers={"Authorization": f"Bearer {token}"})

    server_version = float('.'.join(server_version_resp.text.split(".")[:2]))
    configs = get_available_entity_configs(server_version=server_version)

    extraction_plan = generate_extraction_plan(
        entities=entities if entities is not None else list(configs.keys()),
        entity_configs=configs
    )
    with open(os.path.join(export_directory, 'extraction_plan.json'), 'wt') as f:
        json.dump(dict(
            entity_types=list(configs.keys()),
            server_version_resp=server_version_resp.text,
            server_version=server_version,
            extraction_plan=extraction_plan
        ), f)

    loop = get_event_loop()
    loop.run_until_complete(
        execute_extraction_plan(
            cert=cert,
            entity_configs=configs,
            extraction_plan=extraction_plan,
            directory=export_directory,
            max_threads=max_threads,
            token=token,
            base_url=url
        )
    )
