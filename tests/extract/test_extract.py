from extract import get_available_entity_configs, generate_extraction_plan, run_extract

def test_run_extract(request_mocks, token, server_url, version, edition, output_dir):

    assert run_extract(
        token=token, url=server_url, key_file_path=None, pem_file_path=None, cert_password=None, max_threads=1, export_directory=f'/app/files/{edition}/{version}', entities=None
    )