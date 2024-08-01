from collections import OrderedDict


def deep_merge(source):
    """Recursively merge nested structures."""
    if isinstance(source, dict):
        return OrderedDict((k, deep_merge(v)) for k, v in source.items())
    elif isinstance(source, list):
        return [deep_merge(item) for item in source]
    else:
        return source
