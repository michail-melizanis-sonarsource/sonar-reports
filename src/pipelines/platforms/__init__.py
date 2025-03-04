from importlib import import_module

def get_platform_module(name):
    mod = None
    try:
        mod= import_module(f'pipelines.platforms.{name}')
    except ImportError:
        pass
    return mod