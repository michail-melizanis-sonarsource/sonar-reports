from importlib import import_module


def load_module(mod_type, name):
    mod = None
    try:
        mod = import_module(f'pipelines.{mod_type}.{name}')
    except ImportError:
        pass
    return mod
