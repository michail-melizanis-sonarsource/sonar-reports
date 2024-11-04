from functools import partial
from asyncio import gather
from operations.http_request.base import safe_json_request
from parser import extract_path_value
from math import ceil


async def extract_chunk(max_threads, chunk):
    max_pages = await gather(
        *[get_max_pages(host=chunk[0]['kwargs']['client'], pagination_key=payload['kwargs'].get('paginationKey'),
                        total_key=payload['kwargs'].get('totalKey'),
                        max_page_size=payload['kwargs'].get('maxPageSize'),
                        url=payload['kwargs']['url'], params=payload['kwargs']['params']) for payload in
          chunk]
    )
    pool = list()
    results = []
    for idx, payload in enumerate(chunk):
        page_limit = payload['kwargs'].get('pageLimit')
        results.append(list())
        for params in get_paginated_params(
                pagination_key=payload['kwargs'].get('paginationKey'),
                total_pages=max_pages[idx],
                max_page_size=payload['kwargs'].get('maxPageSize'),
                page_size_key=payload['kwargs'].get('pageSizeKey'),
                params=payload['kwargs']['params'],
                page_limit=page_limit if page_limit else max_pages[idx],
        ):
            partial_func = partial(
                extract_entity_page,
                host=chunk[0]['kwargs']['client'],
                idx=idx,
                result_key=payload['kwargs']['resultKey'],
                url=payload['kwargs']['url'],
                params=params
            )
            pool.append(partial_func)
            if len(pool) >= max_threads:
                output = await gather(*[i() for i in pool])
                for sub_idx, res in output:
                    results[sub_idx].extend(res)
                pool = list()
    if pool:
        output = await gather(*[i() for i in pool])
        for sub_idx, res in output:
            results[sub_idx].extend(res)
    return results


async def get_max_pages(host, url, params, pagination_key, total_key=None, max_page_size=500):
    if pagination_key is None:
        return 1

    status, js = await safe_json_request(
        host=host, method='GET', url=url, params=params
    )
    max_page_size = max_page_size if max_page_size is not None else 500
    total_entities = extract_path_value(path=total_key, obj=js)
    if total_entities is None:
        total_entities = 0
    results_per_page = max_page_size
    total_pages = ceil(total_entities / results_per_page)
    return total_pages


def get_paginated_params(params, pagination_key, page_limit, total_pages, page_size_key, max_page_size):
    if pagination_key is not None:
        for page in range(min(total_pages, page_limit)):
            p = {**params, pagination_key: page + 1}
            if page_size_key:
                p[page_size_key] = max_page_size if max_page_size is not None else 500
            yield p
    else:
        yield params


async def extract_entity_page(host: str, idx, url, result_key, params: dict):
    status, js = await safe_json_request(
        host=host, method='GET', url=url, params=params
    )
    results = list()
    if status is not None and status < 300:
        results = extract_entity_results(js=js, result_key=result_key)
    return idx, results


def extract_entity_results(js, result_key: list | None):
    results = []
    if result_key:
        res = extract_path_value(obj=js, path=result_key)
        if isinstance(res, list):
            results.extend(res)
        elif res:
            results.append(res)
    else:
        results.append(js)
    return results
