import os
from utils import load_csv, export_jsonl
def validate_migration(directory, run_id):
    run_dir = f"{directory}/{run_id}/"
    os.makedirs(run_dir, exist_ok=True)
    completed = set()
    mappings = [
        'organizations',
        'projects',
        'templates',
        'profiles',
        'gates',
        'portfolios',
        'groups'
    ]
    for mapping in mappings:
        name = f'generate{mapping[:-1].capitalize()}Mappings'
        data = load_csv(directory=directory, filename=f'{mapping}.csv')
        export_jsonl(directory=run_dir, name=name, data=data)
        completed.add(name)
    return run_dir, completed