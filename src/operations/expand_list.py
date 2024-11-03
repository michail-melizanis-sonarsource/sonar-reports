def process_chunk(chunk):
    results = list()
    for obj in chunk:
        expanded = execute(inputs=obj['kwargs']['inputs'], result_key=obj['kwargs']['resultKey'])
        results.append(expanded)
    return results

def execute(inputs, result_key, **kwargs):
    results = list()
    if isinstance(inputs, list):
        results = [{result_key: i} for i in inputs]
    return results