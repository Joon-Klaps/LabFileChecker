from rich.text import Text
from rich.table import Table
import pandas as pd

def flatten(list):
    """Flatten a list of lists"""
    return [item for sublist in list for item in sublist]
