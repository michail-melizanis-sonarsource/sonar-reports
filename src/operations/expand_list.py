def process_chunk(chunk):
    results = list()
    for obj in chunk:
        expanded = list()
        if isinstance(obj['inputKey'], list):
            for o in obj['inputKey']:
                expanded.append({obj['outputKey']: o})
        results.append(expanded)
    return results
