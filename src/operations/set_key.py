def process_chunk(chunk):
    return [[execute(**obj['kwargs'])] for obj in chunk]


def execute(key, val):
    return {key: val}
