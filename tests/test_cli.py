import os

from click.testing import CliRunner
from main import cli, extract, report



def test_extract(request_mocks, server_url, token, output_dir):
    runner = CliRunner()
    result = runner.invoke(cli, ['extract', server_url, token, f'--export_directory={output_dir}'])
    assert result.exit_code == 0


def test_report(server_url, extracts, output_dir):
    runner = CliRunner()
    # result = runner.invoke(cli, ['report', server_url, f'--export_directory={output_dir}'])
    report(url=server_url, extract_id=extracts.strip(), export_directory=output_dir)