from operations import load_operation


def parse_field(obj, field_config):
    value = parse_value_field(obj=obj, value_config=field_config["value"])
    for operation_config in field_config.get("operations", []):
        inputs = extract_inputs(obj=obj, operation_config=operation_config)
        operation = load_operation(operation_config["operation"])
        value = operation.execute(*inputs['args'], **inputs['kwargs'])
    return value


def parse_value_field(obj, value_config):
    val = None
    if "raw" in value_config.keys():
        val = value_config["raw"]
    elif "path" in value_config.keys() and isinstance(value_config["path"], str):
        val = extract_path_value(obj=obj[value_config.get('source', 'obj')], path=value_config["path"])
    elif "path" in value_config.keys() and isinstance(value_config["path"], dict):
        path = parse_field(obj=obj, field_config=value_config["path"])
        val = extract_path_value(obj=obj[value_config.get('source', 'obj')], path=path)
    elif "map" in value_config.keys():
        val = dict()
        for k, v in value_config["map"].items():
            val[k] = parse_field(obj=obj, field_config=v)
    elif 'array' in value_config.keys():
        val = [parse_field(obj=obj, field_config=v) for v in value_config['array']]
    return val


def extract_path_value(obj, path: str | list):
    val = None
    if isinstance(path, str):
        if isinstance(obj, dict) and path in obj.keys():
            path = [path]
        else:
            path = path.split('.')
    if path[0] == '$':
        val = obj
    elif isinstance(obj, dict):
        val = obj.get(path[0])
    elif isinstance(obj, list) and not path[0].isnumeric():
        val = [extract_path_value(path=path, obj=o) for o in obj]
    elif isinstance(obj, list) and path[0].isnumeric() and len(obj) > int(path[0]):
        val = obj[int(path[0])]
    if val is not None and len(path) > 1:
        val = extract_path_value(path=path[1:], obj=val)
    return val


def extract_inputs(obj, operation_config):
    args = list()
    kwargs = dict()
    for arg in operation_config.get("args", []):
        args.append(parse_field(obj=obj, field_config=arg))
    for k, v in operation_config.get("kwargs", dict()).items():
        kwargs[k] = parse_field(obj=obj, field_config=v)
    return dict(args=args, kwargs=kwargs)
