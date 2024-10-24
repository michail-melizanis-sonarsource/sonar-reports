import os
import uuid
import json
from copy import deepcopy

from logs import log_event
from dependencies import load_dependencies


def execute_plan(execution_plan, inputs, concurrency, task_configs, output_directory):
    for idx, phase in enumerate(execution_plan):
        log_event(level='WARNING', status='success', process_type='execute_plan', payload=dict(message=f"Executing phase {idx + 1} of {len(execution_plan)}"))

        execute_phase(phase=phase, inputs=inputs, concurrency=concurrency, task_configs=task_configs,
                      output_directory=output_directory)


def execute_phase(phase, inputs, concurrency, task_configs, output_directory):
    for task in phase:
        log_event(level='WARNING', status='success', process_type='execute_phase', payload=dict(message=f"Executing task {task} - {phase.index(task) + 1} of {len(phase)}"))
        execute_task(task=task, task_config=task_configs[task], inputs=inputs, concurrency=concurrency,
                     output_directory=output_directory)


def execute_task(task, concurrency, inputs, task_config, output_directory):
    dependencies = load_dependencies(
        inputs=inputs,
        task=task,
        task_config=task_config,
        concurrency=concurrency,
        output_directory=output_directory
    )
    os.makedirs(f"{output_directory}/{task}", exist_ok=True)

    for idx, chunk in enumerate(dependencies):
        output = True
        for operation_config in task_config['operations']:
            chunk = execute_operation(operation_config=operation_config, idx=idx, chunk=chunk)
            if not chunk:
                output = False
                break
        if output:
            with open(f"{output_directory}/{task}/results.{idx+1}.jsonl", 'wt') as f:
                for i in chunk:
                    f.write(json.dumps(i['obj']) + '\n')


def execute_operation(operation_config, idx, chunk):
    from operations import load_operation
    from parser import extract_inputs
    log_event(level='WARNING', status='success', process_type='execute_task',
              payload=dict(message=f"Executing operation {operation_config['operation']} on chunk {idx + 1}"))
    op = load_operation(name=operation_config['operation'])
    inputs = [extract_inputs(obj=obj, operation_config=operation_config) for obj in chunk]
    res = op.process_chunk(chunk=inputs)
    results = list()
    for idx, r in enumerate(res):
        for obj in r:
            if obj is None:
                continue
            elif isinstance(obj, bool) and obj is True:
                results.append(chunk[idx])
            elif isinstance(obj, dict):
                new_obj = {k:v for k,v in chunk[idx]['obj'].items() if k not in obj.keys()}
                new_obj.update(obj)
                results.append(dict(obj=new_obj, **{k: v for k, v in chunk[idx].items() if k != 'obj'}))
    return results
