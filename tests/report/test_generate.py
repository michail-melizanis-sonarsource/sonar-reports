from extract import run_extract
import pytest


@pytest.fixture()
def extract(request_mocks, token, server_url, version, edition, output_dir):
    return run_extract(
        token=token, url=server_url, key_file_path=None, pem_file_path=None, cert_password=None, max_threads=1,
        export_directory=f'/app/files/{edition}/{version}', entities=None
    )

def test_report(extract, server_url):
    from report.generate import generate_markdown
    assert generate_markdown(url=server_url, extract_directory=extract)