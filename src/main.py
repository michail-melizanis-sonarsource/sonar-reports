import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('url')
@click.argument('token')
@click.option('--concurrency', default=25)
@click.option('--timeout', default=60)
@click.option('--pem_file_path')
@click.option('--key_file_path')
@click.option('--cert_password')
def report(url, token, timeout, concurrency, pem_file_path=None, key_file_path=None, cert_password=None,
           export_directory='/app/files/'):
    from extract import run_extract
    from constants import REPORT_ENTITIES
    from report.generate import generate_markdown
    if not url.endswith('/'):
        url = f"{url}/"
    run_extract(
        token=token, url=url, pem_file_path=pem_file_path, key_file_path=key_file_path, max_threads=concurrency,
        cert_password=cert_password, export_directory=export_directory, entities=REPORT_ENTITIES,
        timeout=timeout
    )
    generate_markdown(url=url, extract_directory=export_directory)


if __name__ == '__main__':
    cli()
