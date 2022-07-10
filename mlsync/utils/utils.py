import yaml
import time


def timestamp_epoch_to_datetime(timestamp):
    """Converts a timestamp to a datetime

    Args:
        timestamp (int): The timestamp to convert.
    """
    return time.strftime("%a, %d %b %H:%M:%S", time.localtime(timestamp))


def yaml_loader(filepath):
    """Loads a YAML file as Python Dict

    Args:
        filepath (str): The path to the YAML file.
    """
    with open(filepath, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def yaml_dumper(data, filepath):
    """Dumps a Python Dict as YAML

    Args:
        data (dict): The Python Dict to dump.
        filepath (str): The path to the output YAML file.
    """
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def find_key(obj, key):
    """Finds a key in a nested dictionary

    Args:
        obj (dict): The Python Dict to search.
        key (str): The key to search for.
    """
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            return find_key(v, key)


def url_remove_trailing_slug(url):
    """Removes the trailing slug from a URL

    Args:
        url (str): The URL to remove the trailing slug from.
    """
    url = url.split("/")
    url.pop()
    url = "/".join(url)
    return url


def typify(value, val_type):
    """Typifies a value.
        Supported types:
        - int
        - float
        - str
        - bool
        - select
        - timestamp

    Args:
        value (str): The value to typify.
        val_type (str): The type of the value.
    """
    try:
        if val_type == "int" or val_type == "integer":
            value = int(value)
        elif val_type == "float":
            value = float(value)
        elif val_type == "bool":
            value = bool(value)
        elif val_type == "str" or val_type == "string":
            value = str(value)
        elif val_type == "select":
            pass
        elif val_type == "timestamp":
            value = timestamp_epoch_to_datetime(value)
        else:
            print("WARNING: Unsupported value type: " + val_type)
    except Exception as e:
        print(f"WARNING: Failed to typify value {value} to {val_type} due to {e}")
    return value
