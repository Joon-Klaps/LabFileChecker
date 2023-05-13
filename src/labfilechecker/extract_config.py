import yaml
import pandas as pd

def extract_config(config):
    """Extract config from config file."""
    if config.endswith(".yml"):
        return extract_config_yml(config)
    elif config.endswith(".xlsx"):
        return extract_config_excel(config)
    else:
        raise ValueError("Unknown config file type")

def extract_config_excel(config):
    """Extract config from config file."""
    df = pd.read_excel(config, sheet_name="config")
    return df.to_dict()

def extract_config_yml(config):
    """Extract config from config file."""

    with open(config, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise Exception(exc)
        pass
