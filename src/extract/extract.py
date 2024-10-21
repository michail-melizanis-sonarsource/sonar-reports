import uuid
from collections import defaultdict

from httpx import AsyncClient, Limits
from asyncio import gather
import os
import json
from math import ceil
from functools import partial

from extract.utils import generate_auth_headers
from logs import log_event
from utils import extract_path_value, entity_reader
from itertools import product


async def execute_extraction_plan(token: str, server_version: float, directory: str, base_url: str,
                                  extraction_plan: list, entity_configs: dict, cert: tuple[str, str, str] | None,
                                  max_threads: int, timeout=60):
    limits = Limits(max_connections=max_threads * 2, max_keepalive_connections=max_threads * 2)

    async with AsyncClient(
            base_url=base_url,
            cert=cert,
            limits=limits,
            timeout=timeout,
            headers=generate_auth_headers(token=token, server_version=server_version)
    ) as client:
        for phase in extraction_plan:
            for entity in phase:
                await extract_entity(client=client, config=entity_configs[entity], max_threads=max_threads,
                                     directory=directory, entity=entity)
    return True


async def extract_entity(config, client, max_threads, entity, directory):
    entity_dir = f'{directory}/{entity}'
    os.makedirs(entity_dir, exist_ok=True)
    chunk = list()
    chunk_number = 0
    for idx, dependencies in enumerate(generate_entity_plan(directory=directory, config=config, entity=entity)):

        initial_params = load_params(config=config, dependencies=dependencies)
        chunk.append(dict(params=initial_params, dependencies=dependencies))
        if len(chunk) >= max_threads:
            log_event(level='WARNING', event=f"Extracting {entity} chunk {chunk_number+1}")
            chunk_number += 1
            await extract_chunk(client=client, max_threads=max_threads, config=config, chunk=chunk,
                                entity_dir=entity_dir)
            chunk = list()
    if chunk:
        log_event(level='WARNING', event=f"Extracting {entity} chunk {chunk_number + 1}")
        await extract_chunk(client=client, config=config, max_threads=max_threads, chunk=chunk, entity_dir=entity_dir)


async def extract_chunk(client, max_threads, config, chunk, entity_dir):
    max_pages = await gather(
        *[get_max_pages(client=client, config=config, params=payload['params']) for payload in chunk]
    )
    pool = list()
    page = 1
    for idx, payload in enumerate(chunk):
        for params in get_paginated(config=config, total_pages=max_pages[idx], params=payload['params']):
            partial_func = partial(
                extract_entity_page,
                client=client,
                config=config,
                dependencies=payload['dependencies'],
                params=params
            )
            pool.append(partial_func)
            if len(pool) >= max_threads:
                results = await gather(*[i() for i in pool])
                store_results(results=results, page=str(uuid.uuid4()), directory=entity_dir, config=config)
                page += 1
                pool = list()
    if pool:
        results = await gather(*[i() for i in pool])
        store_results(results=results, page=str(uuid.uuid4()), directory=entity_dir, config=config)


def store_results(config, results, page, directory):
    if not any(results):
        return
    with open(f'{directory}/results.{page}.jsonl', 'wt') as f:
        for result in results:
            for row in result:
                if not filter_result(config=config, result=row):
                    continue
                f.write(json.dumps(row) + '\n')


async def get_max_pages(client, config, params):
    if config.get('paginationKey') is None:
        return 1
    response = await client.get(config['url'], params=params)

    try:
        first_page = response.json()
    except Exception as e:
        log_event(level='ERROR',
                  event=dict(status_code=response.status_code, content=response.content, url=config['url'],
                             params=params))
        raise e
    try:
        total_entities = extract_path_value(path=config['totalKey'], js=first_page)
        if total_entities is None:
            total_entities = 0
        results_per_page = config.get('maxPageSize', 1)
        total_pages = ceil(total_entities / results_per_page)
    except Exception as e:
        log_event(level='ERROR',
                  event=response.json())
        raise e
    return total_pages


def get_paginated(params, config, total_pages):
    if config.get('paginationKey') is not None:
        for page in range(min(total_pages, config.get('pageLimit', total_pages))):
            yield {**params, config['paginationKey']: page + 1}
    else:
        yield params


def generate_entity_plan(entity, config, directory):
    for dependencies in load_dependencies(entity=entity, config=config, directory=directory):
        if not filter_dependencies(config=config, dependencies=dependencies):
            continue
        yield dependencies


def filter_dependencies(config, dependencies):
    allowed = True
    for filter_ in config.get("preFilters", []):
        value = extract_path_value(path=filter_['path'], js=dependencies[filter_['source']])
        allowed = evaluate_filter(filter_=filter_, value=value)
        if not allowed:
            break
    return allowed


def filter_result(config, result):
    allowed = True
    for filter_ in config.get("postFilters", []):
        value = extract_path_value(path=filter_['path'], js=result)
        allowed = evaluate_filter(filter_=filter_, value=value)
        if not allowed:
            break
    return allowed


def evaluate_filter(filter_, value):
    allowed = True
    if filter_['operator'] == 'neq':
        allowed = value != filter_['value']
    elif filter_['operator'] == 'eq':
        allowed = value == filter_['value']
    elif filter_['operator'] == 'nin':
        allowed = value not in filter_['value']
    elif filter_['operator'] == 'in':
        allowed = value in filter_['value']
    return allowed


async def extract_entity_page(client: AsyncClient, config: dict, params: dict, dependencies: dict):
    response = await client.get(config['url'], params=params)
    if response.status_code >= 300:
        return []
    try:
        results = extract_entity_results(js=response.json(), dependencies=dependencies, config=config)
    except Exception as e:
        log_event(level='ERROR', event=e)
        raise e
    return results


def extract_entity_results(js, dependencies, config):
    results = []
    if config.get('resultKeys', []):
        for result_key in config['resultKeys']:
            if isinstance(js[result_key], dict):
                for k, v in js[result_key].items():
                    i = dict(indexKey=k, values=v)
                    if config.get('skipKey'):
                        if i.get(config['skipKey']):
                            continue
                    i = apply_operations(config=config, js=i, dependencies=dependencies)
                    results.append(i)
            elif isinstance(js[result_key], list):
                for i in js[result_key]:
                    if config.get('skipKey'):
                        if i.get(config['skipKey']):
                            continue
                    i = apply_operations(config=config, js=i, dependencies=dependencies)
                    results.append(i)
            else:
                i = apply_operations(config=config, js=js[result_key], dependencies=dependencies)
                results.append(i)
    else:
        js = apply_operations(config=config, js=js, dependencies=dependencies)
        results.append(js)
    return results


def apply_operations(config, js, dependencies):
    for operation in config.get('operations', []):
        if operation['operator'] == 'set':
            js[operation['key']] = extract_path_value(path=operation['value']['path'],
                                                      js=dependencies[operation['value']['source']])
    return js


def load_params(config, dependencies):
    params = dict()
    if 'maxPageSize' in config.keys():
        params[config['pageSizeKey']] = config['maxPageSize']
    for k, v in config.get('parameters', dict()).items():
        if 'source' in v.keys() and isinstance(dependencies[v['source']], dict):
            params[k] = extract_path_value(path=v['path'], js=dependencies[v['source']])
        if 'source' in v.keys() and isinstance(dependencies[v['source']], list):
            params[k] = v['joinCharacter'].join(
                [extract_path_value(path=v['path'], js=i) for i in dependencies[v['source']]])
        elif "value" in v.keys():
            params[k] = v['value']
    return params


def load_dependencies(entity, config, directory):
    from functools import partial
    required_keys = plan_dependency_values(config=config, entity=entity)
    load_funcs = [
        partial(
            load_dependency,
            dependency=dependency,
            directory=directory,
            required_keys=required_keys[dependency['key']]
        )
        for dependency in config.get('dependencies', [])
    ]
    if len(load_funcs) == 0:
        yield dict()
    else:
        if len(load_funcs) > 1:
            loader = partial(product, *[i() for i in load_funcs])
        else:
            loader = load_funcs[0]
        for dependencies in loader():
            if any(len(dependency) == 0 for dependency in dependencies):
                continue
            dependency_map = dict()
            if len(load_funcs) == 1:
                dependencies = [dependencies]
            for idx, dependency in enumerate(config.get('dependencies', [])):
                dependency_map[dependency['key']] = dependencies[idx]
            yield dependency_map


def load_dependency(dependency, directory, required_keys):
    load_strategy = dependency.get('loadStrategy', 'each')
    if load_strategy == 'each':
        for entity in entity_reader(extract_directory=directory, entity_type=dependency['key']):
            yield entity
    elif load_strategy == 'chunk':
        entities = list()
        for entity in entity_reader(extract_directory=directory, entity_type=dependency['key']):
            results = clean_entity(entity=entity, required_keys=required_keys)
            entities.append(results)
            if len(entities) >= dependency['chunkSize']:
                yield entities
                entities = list()
        if entities:
            yield entities
    elif load_strategy == 'all':
        entities = list()
        for entity in entity_reader(extract_directory=directory, entity_type=dependency['key']):
            results = clean_entity(entity=entity, required_keys=required_keys)
            entities.append(results)
        yield entities


def clean_entity(entity, required_keys):
    return {k: v for k, v in entity.items() if k in required_keys}


def find_required_keys(entity, field):
    required_keys = defaultdict(set)
    if isinstance(field, dict):
        for k, v in field.items():
            if isinstance(v, dict):
                sub_keys = find_required_keys(field=v, entity=entity)
                for sub_key, keys in sub_keys.items():
                    required_keys[sub_key] = required_keys[sub_key].union(keys)
            elif k == 'path':
                if 'source' in field.keys():
                    required_keys[field['source']].add(v.replace('$.', '').split('.')[0])
                else:
                    required_keys[entity].add(v.replace('$.', '').split('.')[0])
    elif isinstance(field, list):
        for i in field:
            sub_keys = find_required_keys(field=i, entity=entity)
            for sub_key, keys in sub_keys.items():
                required_keys[sub_key] = required_keys[sub_key].union(keys)
    return required_keys


def plan_dependency_values(config, entity):
    field_keys = ['operations', 'prefilters', 'parameters', 'json']
    required_keys = defaultdict(set)
    for key in field_keys:
        if key in config.keys():
            requirements = find_required_keys(entity=entity, field=config[key])
            for k, v in requirements.items():
                required_keys[k] = required_keys[k].union(v)
    return required_keys
