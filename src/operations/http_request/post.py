from asyncio import gather
from parser import extract_path_value
from operations.http_request.base import safe_json_request


async def create_chunk(chunk, max_threads):
    results = await gather(
        *[
            safe_json_request(
                host=chunk[0]['kwargs']['client'],
                method='POST',
                raise_over=300,
                url=payload['kwargs']['url'],
                data={k:v for k,v in payload['kwargs']['payload'].items() if v is not None} if payload['kwargs']['encoding'] == 'x-www-form-urlencoded' else None,
                json={k:v for k,v in payload['kwargs']['payload'].items() if v is not None} if payload['kwargs']['encoding'] == 'json' else None,
            ) for payload in chunk
        ]
    )
    return [[extract_path_value(obj=result[1], path=chunk[idx]['kwargs']['resultKey'])] for idx, result in
            enumerate(results)]
