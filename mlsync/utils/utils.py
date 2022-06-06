import yaml

def yaml_loader(filepath):
    """Loads a YAML file as Python Dict"""
    with open(filepath, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def yaml_dumper(data, filepath):
    """Dumps a Python Dict as YAML"""
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def find_key(obj, key):
    """Finds a key in a nested dictionary"""
    if key in obj: return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            return find_key(v, key)
