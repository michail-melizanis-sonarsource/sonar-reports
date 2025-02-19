import os

from click.testing import CliRunner
from main import cli


def test_extract(request_mocks, server_url, token, output_dir):
    runner = CliRunner()
    result = runner.invoke(cli, ['extract', server_url, token, f'--export_directory={output_dir}'], catch_exceptions=False)
    assert result.exit_code == 0


def test_report(server_url, extracts, report_output_dir, report_type):
    runner = CliRunner()
    result = runner.invoke(cli, ['report', f'--export_directory={report_output_dir}', f'--report_type={report_type}'],
                           catch_exceptions=False)
    assert result.exit_code == 0


def test_report_completes_with_empty_results(server_url, empty_results, report_type):
    runner = CliRunner()
    result = runner.invoke(cli, ['report', f'--export_directory={empty_results}', f'--report_type={report_type}'],
                           catch_exceptions=False)
    assert result.exit_code == 0


def test_structure(server_url, extracts, output_dir):
    runner = CliRunner()
    result = runner.invoke(cli, ['structure', f'--export_directory={output_dir}'], catch_exceptions=False)
    assert result.exit_code == 0


def test_structure_completes_with_empty_results(server_url, empty_results):
    runner = CliRunner()
    result = runner.invoke(cli, ['structure', f'--export_directory={empty_results}'], catch_exceptions=False)
    assert result.exit_code == 0


def test_mappings(server_url, extracts, output_dir):
    runner = CliRunner()
    runner.invoke(cli, ['structure', f'--export_directory={output_dir}'], catch_exceptions=False)
    result = runner.invoke(cli, ['mappings', f'--export_directory={output_dir}'], catch_exceptions=False)
    assert result.exit_code == 0

def test_mappings_completes_with_empty_results(server_url, empty_results):
    runner = CliRunner()
    runner.invoke(cli, ['structure', f'--export_directory={empty_results}'], catch_exceptions=False)
    result = runner.invoke(cli, ['mappings', f'--export_directory={empty_results}'], catch_exceptions=False)
    assert result.exit_code == 0
