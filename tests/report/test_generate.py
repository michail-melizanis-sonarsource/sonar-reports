from extract import run_extract
import pytest


def test_report(server_url, edition, version, extracts):
    from report.generate import generate_markdown
    assert generate_markdown(url=server_url, extract_directory=extracts[1])
