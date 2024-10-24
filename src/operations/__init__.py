from importlib import import_module


def load_operation(name):
    return import_module(f'operations.{name}', name)
