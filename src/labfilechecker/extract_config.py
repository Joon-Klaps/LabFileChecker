import yaml
import pandas as pd

def extract_config(config):
    """
    Extract config from config file.
    
    Parameters:
        config (str): path to config file, a df in excel or a .yml file structured like this 
            {'index1': {'col1': 1, 'col2': 0.5}, 'index2': {'col1': 2, 'col2': 0.75}}

    Returns:
        config (dict): config as a dictionary with a structure like this:
            {'index1': {'col1': 1, 'col2': 0.5}, 'index2': {'col1': 2, 'col2': 0.75}}
    """
    if config.endswith(".yml"):
        return extract_config_yml(config)
    elif config.endswith(".xlsx"):
        return extract_config_excel(config)
    else:
        raise ValueError("Unknown config file type")

def extract_config_excel(config):
    df = pd.read_excel(config, sheet_name="config", na_values=["", "NA", " ", "nan", "NaN", "NAN"])
    # return a dictionary that doesn't contain any NaN values in the values
    return {k: v for row_dict in df.to_dict('index') for k, v in row_dict.items() if v == v and v is not None}

def extract_config_yml(config):
    """Extract config from config file."""

    with open(config, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise Exception(exc)
        pass
