def execute(strings, delimiter, skip_empty_string=False, **kwargs):
    if any([s is None for s in strings]):
        return None
    if skip_empty_string and any([not s for s in strings]):
        return None
    return delimiter.join(strings)

