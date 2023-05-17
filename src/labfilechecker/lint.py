#!/usr/env python
"""My main script to check for inconsistencies in lab (excel) files."""

import logging
import os 

import rich
import rich.progress
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.emoji import Emoji

from utils import flatten

import pandas as pd

from extract_config import extract_config
import lint_tests 

class ExcelLint:
    """Class to check for inconsistencies in lab (excel) files."""
    
    def __init__(self, config:str, file:str,skiprows:int):
        """Initialize the class."""        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        config = config if config != "config sheet in [file]" else file 
        self.logger.info("Using config in %s", config)
        self.config = extract_config(config)
        self.skiprows = skiprows

        self.logger.info("Using excel in %s", file )
        df = pd.read_excel(file, skiprows=self.skiprows)
        df  = df.reset_index().rename(columns={'index': 'Row_Number'})
        df['Row_Number'] = df['Row_Number'] + self.skiprows +2 
        self.df = df
        
        self.lint_tests = {
            "column_names"        : lint_tests.column_names,
            "duplicate_samples"   : lint_tests.duplicate_samples,
            "dates"               : lint_tests.dates,
            "unrealistic_dates"   : lint_tests.unrealistic_dates,
            "numeric_values"      : lint_tests.numeric_values,
            "presence_patientsID" : lint_tests.presence_patientsID,
            "referring_ids"       : lint_tests.referring_ids,
            "allowed_values"      : lint_tests.allowed_values
            }
        self.passed = []
        self.warned = []
        self.failed = []

    def lint(self):
        """Run all lint tests."""
        passed = []
        warned = []
        failed = []

        # TOD progress bar
        for key, lint_test in self.lint_tests.items():
            self.logger.info("Running test %s", key)
            passed,warned,failed = lint_test(self.df.copy(), self.config)
            self.passed.extend(passed)
            self.warned.extend(warned)
            self.failed.extend(failed)
        pass 

    def _print_results(self):
        """Print linting results to the command line.

        Uses the ``rich`` library to print a set of formatted tables to the command line
        summarising the linting results.
        """

        console = Console(force_terminal=True)

        # Helper function to format test links nicely
        def format_result(test_results, color ):
            """Format a list of lint test results into a rich table."""
            table = Table(show_header=True, header_style=f"bold {color}",style=f"{color}" )
            table.add_column("Row")
            table.add_column("Column")
            table.add_column("Value")
            table.add_column("Test")
            table.add_column("Message")

            for result in test_results:
                row = str(result.row) if result.row is not None else ""
                value = str(result.value) if result.value is not None else ""
                column = str(result.column) if result.column is not None else ""
                table.add_row(
                    row,
                    column,
                    value,
                    result.lint_test,
                    result.message,
                )
            return table

        # Table of warning tests
        if len(self.warned) > 0:
            console.print(
                rich.panel.Panel(
                    format_result(self.warned, "yellow"),
                    title=rf"[bold][!] {len(self.warned)} Tests Warning",
                    title_align="left",
                    style="yellow",
                    padding=1,
                )
            )

        # Table of failing tests
        if len(self.failed) > 0:
            console.print(
                rich.panel.Panel(
                    format_result(self.failed, "red"),
                    title=rf"[bold][✗] {len(self.failed)} Tests Failed",
                    title_align="left",
                    style="red",
                    padding=1,
                )
            )
        # Table of passed tests
        if len(self.passed) > 0:
            console.print(
                rich.panel.Panel(
                    format_result(self.passed, "green"),
                    title=rf"[bold][✔] {len(self.passed)} Tests Passed",
                    title_align="left",
                    style="green",
                    padding=1,
                )
            )
        
        # make a summary table printing the number of passed, warned and failed tests
        summary_table = Table(show_header=True, header_style="bold blue",style="blue" )
        summary_table.add_column("Passed")
        summary_table.add_column("Warned")
        summary_table.add_column("Failed")
        summary_table.add_row(
            str(len(self.passed)),
            str(len(self.warned)),
            str(len(self.failed)),
        )
        console.print(
            rich.panel.Panel(
                summary_table,
                title=rf"[bold]Summary",
                title_align="left",
                style="blue",
                padding=1,
            )
        )

        if len(self.warned) + len(self.failed) == 0:
            console.print("😎 All tests passed! :tada::tada::tada:")

