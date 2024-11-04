def process_chunk(chunk):
    results = []
    for obj in chunk:
        if execute(**obj['kwargs']):
            results.append([True])
        else:
            results.append([])
    return results


def execute(left, right, operator):
    allowed = True
    if operator == 'neq':
        allowed = left != right
    elif operator == 'eq':
        allowed = left == right
    elif operator == 'nin':
        allowed = left not in right
    elif operator == 'in':
        allowed = left in right
    elif operator == 'gt':
        allowed = left > right
    elif operator == 'lt':
        allowed = left < right
    elif operator == 'gte':
        allowed = left >= right
    elif operator == 'lte':
        allowed = left <= right
    return allowed
