from parser import extract_path_value


def process_yaml(file):
    pipelines = list()
    root_path = '$'
    for key, job in extract_path_value(path='jobs', obj=file['yaml'], default=dict()).items():
        pipelines.append(process_job(
            job=job,
            root_path=root_path + f'.jobs.{key}'
        ))
    return pipelines


def process_job(job, root_path):
    pipeline = dict(
        runtime=job.get('runs-on', 'ubuntu'),
        runs_sonar=False,
        variables=process_variables(root_path=root_path, env_section=job.get('env', dict())),
        working_dir=extract_path_value(obj=job, path='defaults.run.working-directory', default='./'),
        tasks=list(),
    )
    for idx, step in enumerate(extract_path_value(obj=job, path='steps', default=list())):
        task = process_step(
                root_path=root_path + f'.steps.{idx}',
                runtime=pipeline['runtime'],
                step=step,
                default_working_dir=pipeline['working_dir'],
            )
        if task['runs_sonar']:
            pipeline['runs_sonar'] = True
            pipeline['tasks'].append(task)
    return pipeline


def process_step(root_path, step, default_working_dir, runtime):
    task = dict(
        path = root_path,
        variables=process_variables(root_path=root_path, env_section=step.get('env', dict())),
        plugin_path=f'{root_path}.uses',
        app= extract_path_value(obj=step, path='uses', default=''),
        runner='',
        script='',
        working_dir=extract_path_value(obj=step, path='working-directory', default=default_working_dir),
        runs_sonar=False,
    )
    if 'sonar' in task['app']:
        task['runs_sonar'] = True
        task['runner'] = 'plugin'
        if extract_path_value(obj=step, path='with.args'):
            task['script'] = f'{root_path}.with.args'
    else:
        task['script'] = f'{root_path}.run'
        task['runner'] = 'script'
        script = extract_path_value(obj=step, path='run', default='')
        if any([cmd in script.lower() for cmd in ['sonar-scanner', 'maven', 'gradle']]):
            task['runs_sonar'] = True
    return task


def process_variables(root_path, env_section):
    variables = dict()
    for env in env_section.keys():
        if env.startswith('SONAR_'):
            variables[env] = f'{root_path}.env.{env}'
    return variables

def format_variable(value, var_type):
    if var_type == 'secret':
        return "${{ " + 'secrets.' + value + " }}"
    else:
        return "${{ " + 'vars.' + value + " }}"

def is_valid_pipeline(file):
    return True