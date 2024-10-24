from asyncio import gather
from parser import extract_path_value
from operations.http_request.base import safe_json_request


async def create_chunk(chunk):
    results = await gather(
        *[
            safe_json_request(
                host=chunk[0]['kwargs']['client'],
                method='POST',
                url=payload['kwargs']['url'],
                data=payload['kwargs']['payload'] if payload['kwargs']['encoding'] == 'x-www-form-urlencoded' else None,
                json=payload['kwargs']['payload'] if payload['kwargs']['encoding'] == 'json' else None,
            ) for payload in chunk
        ]
    )
    return [[extract_path_value(obj=result.json(), path=chunk[idx]['kwargs']['resultKey'])] for idx, result in
            enumerate(results)]
