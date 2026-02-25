from importlib import import_module


def import_string(dotted_path: str):
    module_path, attr = dotted_path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, attr)
