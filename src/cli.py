import click
import json
from report import generate_markdown

@click.command()
@click.argument('input_file')
@click.argument('output_file')
# @click.option('--export_directory')
def extract(input_file='/app/files/input.json', output_file='/app/files/output.md'):
    with open(input_file, 'rt') as f:
        data = json.load(f)
    md = generate_markdown(config=data)
    with open(output_file, 'wt') as w:
        w.write(md)

if __name__ == '__main__':
    extract()
