def execute(input_list, result_list, dedupe=True, **kwargs):
    if not (isinstance(input_list, list) and isinstance(result_list, list)):
        return result_list
    result_list.extend(input_list)
    if dedupe:
        result_list = list(set(result_list))
    return result_list
