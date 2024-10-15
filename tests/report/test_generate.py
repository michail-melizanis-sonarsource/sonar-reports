from extract import run_extract
import pytest


def test_report(server_url, edition, version):
    from report.generate import generate_markdown
    assert generate_markdown(url=server_url, extract_directory=f'/app/files/{edition}/{version}')
