from collections import defaultdict

from utils import multi_extract_object_reader
from datetime import datetime, UTC, timedelta
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


def process_task(server_id, tasks, task):
    if task['type'] not in tasks[server_id].keys():
        tasks[server_id][task['type']] = create_task_template(server_id=server_id, task_type=task['type'])
    submitted_time = datetime.strptime(task['submittedAt'], '%Y-%m-%dT%H:%M:%S%z')
    started_time = datetime.strptime(task['startedAt'], '%Y-%m-%dT%H:%M:%S%z')
    queue_time_ms = (started_time - submitted_time).total_seconds() * 1000
    execution_time_ms = task['executionTimeMs']
    tasks[server_id][task['type']]['total'] += 1
    tasks[server_id][task['type']]['succeeded'] += task['status'] == 'SUCCESS'
    tasks[server_id][task['type']]['failed'] += task['status'] == 'FAILED'
    tasks[server_id][task['type']]['canceled'] += task['status'] == 'CANCELED'
    if tasks[server_id][task['type']]['total'] > 1:
        tasks[server_id][task['type']]['min_queue_time'] = min(tasks[server_id][task['type']]['min_queue_time'],
                                                               queue_time_ms)
        tasks[server_id][task['type']]['max_queue_time'] = max(tasks[server_id][task['type']]['max_queue_time'],
                                                               queue_time_ms)
        tasks[server_id][task['type']]['min_execution_time'] = min(tasks[server_id][task['type']]['min_execution_time'],
                                                                   execution_time_ms)
        tasks[server_id][task['type']]['max_execution_time'] = max(tasks[server_id][task['type']]['max_execution_time'],
                                                                   execution_time_ms)
        tasks[server_id][task['type']]['first_run'] = min(tasks[server_id][task['type']]['first_run'], started_time)
        tasks[server_id][task['type']]['last_run'] = max(tasks[server_id][task['type']]['last_run'], started_time)
    else:
        tasks[server_id][task['type']]['min_queue_time'] = queue_time_ms
        tasks[server_id][task['type']]['max_queue_time'] = queue_time_ms
        tasks[server_id][task['type']]['min_execution_time'] = execution_time_ms
        tasks[server_id][task['type']]['max_execution_time'] = execution_time_ms
        tasks[server_id][task['type']]['first_run'] = started_time
        tasks[server_id][task['type']]['last_run'] = started_time

    tasks[server_id][task['type']]['total_queue_time'] += queue_time_ms
    tasks[server_id][task['type']]['avg_queue_time'] = tasks[server_id][task['type']]['total_queue_time'] / \
                                                       tasks[server_id][task['type']]['total']
    tasks[server_id][task['type']]['total_execution_time'] += execution_time_ms
    tasks[server_id][task['type']]['avg_execution_time'] = tasks[server_id][task['type']]['total_execution_time'] / \
                                                           tasks[server_id][task['type']]['total']
    return tasks


def process_tasks(directory, extract_mapping, server_id_mapping):
    tasks = defaultdict(dict)
    for key in ['getTasks', 'getProjectTasks']:
        for url, task in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key=key):
            server_id = server_id_mapping[url]
            if 'type' not in task.keys():
                print(task)
                continue
            tasks = process_task(server_id=server_id, tasks=tasks, task=task)
    return tasks


def generate_task_markdown(directory, extract_mapping, server_id_mapping):
    tasks = process_tasks(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    rows = [
        dict(
            server_id=server_id,
            type=task_type,
            total=task['total'],
            succeeded=task['succeeded'],
            failed=task['failed'],
            canceled=task['canceled'],
            min_queue_time=task['min_queue_time'],
            max_queue_time=task['max_queue_time'],
            avg_queue_time=task['avg_queue_time'],
            min_execution_time=task['min_execution_time'],
            max_execution_time=task['max_execution_time'],
            avg_execution_time=task['avg_execution_time'],
            first_run=task['first_run'].strftime('%Y-%m-%d'),
            last_run=task['last_run'].strftime('%Y-%m-%d')
        ) for server_id, tasks in tasks.items() for task_type, task in tasks.items()
    ]
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
        rows=rows
    )
