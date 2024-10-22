import os.path

from extract import run_extract


def test_run_extract(request_mocks, token, server_url, version, edition, output_dir):
    extract_id, extract_dir =  run_extract(
        token=token, url=server_url, key_file_path=None, pem_file_path=None, cert_password=None, max_threads=1,
        export_directory=f'/app/files/{edition}/{version}', entities=None, timeout=60,
    )
    assert os.path.exists(extract_dir)

def test_resume_extract(request_mocks, token, server_url, version, edition, output_dir, extracts):
    extract_id, extract_dir = run_extract(
        token=token, url=server_url, key_file_path=None, pem_file_path=None, cert_password=None, max_threads=25,
        export_directory=f'/app/files/{edition}/{version}', entities=None, timeout=60, extract_id=extracts[0]
    )
    assert extract_dir
