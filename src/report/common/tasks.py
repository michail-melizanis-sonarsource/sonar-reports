from collections import defaultdict

from parser import extract_path_value
from utils import multi_extract_object_reader
from datetime import datetime
from report.utils import generate_section


def create_task_template(server_id, task_type):
    return dict(
        server_id=server_id,
        type=task_type,
        total=0,
        succeeded=0,
        failed=0,
        canceled=0,
        min_queue_time=0,
        max_queue_time=0,
        total_queue_time=0,
        avg_queue_time=0,
        min_execution_time=0,
        max_execution_time=0,
        total_execution_time=0,
        avg_execution_time=0,
        first_run=None,
        last_run=None,
    )


def process_task(server_id, tasks, task, task_type):

    server_task = tasks[server_id][task_type]
    server_task.update(
        dict(
            type=task_type,
            server_id=server_id,
        )
    )
    submitted_time = extract_path_value(obj=task, path='$.submittedAt')
    started_time = extract_path_value(obj=task, path='$.startedAt')
    try:
        submitted_time = datetime.strptime(submitted_time, '%Y-%m-%dT%H:%M:%S%z')
        started_time = datetime.strptime(started_time, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        return tasks

    execution_time_ms = extract_path_value(obj=task, path='$.executionTimeMs')
    queue_time_ms = (started_time - submitted_time).total_seconds() * 1000
    server_task['total'] += 1
    server_task['succeeded'] += task['status'] == 'SUCCESS'
    server_task['failed'] += task['status'] == 'FAILED'
    server_task['canceled'] += task['status'] == 'CANCELED'
    if server_task['total'] > 1:
        server_task['min_queue_time'] = min(server_task['min_queue_time'],queue_time_ms)
        server_task['max_queue_time'] = max(server_task['max_queue_time'],queue_time_ms)
        server_task['min_execution_time'] = min(server_task['min_execution_time'],execution_time_ms)
        server_task['max_execution_time'] = max(server_task['max_execution_time'],execution_time_ms)
        server_task['first_run'] = min(server_task['first_run'], started_time)
        server_task['last_run'] = max(server_task['last_run'], started_time)
    else:
        server_task['min_queue_time'] = queue_time_ms
        server_task['max_queue_time'] = queue_time_ms
        server_task['min_execution_time'] = execution_time_ms
        server_task['max_execution_time'] = execution_time_ms
        server_task['first_run'] = started_time
        server_task['last_run'] = started_time

    server_task['total_queue_time'] += queue_time_ms
    server_task['avg_queue_time'] = server_task['total_queue_time'] / server_task['total']
    server_task['total_execution_time'] += execution_time_ms
    server_task['avg_execution_time'] = server_task['total_execution_time'] / server_task['total']
    return tasks


def process_tasks(directory, extract_mapping, server_id_mapping):
    tasks = defaultdict(lambda: defaultdict(lambda: dict(
        server_id=None,
        type=None,
        total=0,
        succeeded=0,
        failed=0,
        canceled=0,
        min_queue_time=0,
        max_queue_time=0,
        total_queue_time=0,
        avg_queue_time=0,
        min_execution_time=0,
        max_execution_time=0,
        total_execution_time=0,
        avg_execution_time=0,
        first_run=None,
        last_run=None,
    )))
    for key in ['getTasks', 'getProjectTasks']:
        for url, task in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key=key):
            server_id = server_id_mapping[url]
            task_type = extract_path_value(obj=task, path='$.type')
            if not task_type:
                continue
            tasks = process_task(server_id=server_id, tasks=tasks, task=task, task_type=task_type)
    return tasks


def generate_task_markdown(directory, extract_mapping, server_id_mapping):
    tasks = process_tasks(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    return generate_section(
        title='Tasks (Past 30 Days)',
        headers_mapping={
            "Server ID": "server_id",
            "Type": "type",
            "Total": "total",
            "Succeeded": "succeeded",
            "Failed": "failed",
            "Canceled": "canceled",
            "Min Queue Time (ms)": "min_queue_time",
            "Max Queue Time (ms)": "max_queue_time",
            "Avg Queue Time (ms)": "avg_queue_time",
            "Min Execution Time (ms)": "min_execution_time",
            "Max Execution Time (ms)": "max_execution_time",
            "Avg Execution Time (ms)": "avg_execution_time",
            "First Run": "first_run",
            "Last Run": "last_run"
        },
        rows=[task for server_id, tasks in tasks.items() for task_type, task in tasks.items()]
    )
