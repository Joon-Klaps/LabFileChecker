#!/usr/env python
"""My main script to check for inconsistencies in lab (excel) files."""

import logging
import os 

import rich
import rich.progress
from rich.console import Console,group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

import pandas as pd

from extract_config import extract_config
import lint_tests 

class LintResult:
    """An object to hold the results of a lint test"""

    def __init__(self, row, value, lint_test, message):
        self.row  = row
        self.value = value
        self.lint_test = lint_test
        self.message = message

    

class ExcelLint:
    """Class to check for inconsistencies in lab (excel) files."""
    
    def __init__(self, config:str, file:str):
        """Initialize the class."""        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        config = config if config != "config sheet in [file]" else file 
        self.logger.info("Using config in %s", config)
        self.config = extract_config(config)

        self.logger.info("Using excel in %s", file )
        self.df = pd.read_excel(file, skiprows=)
        
        self.passed = []
        self.warned = []
        self.failed = []
        self.lint_tests = {
            "column_names"        : lint_tests.column_names,
            "duplicate_samples"   : lint_tests.duplicate_samples,
            "dates"               : lint_tests.dates,
            "numeric_values"      : lint_tests.numeric_values,
            "presence_patientsID" : lint_tests.presence_patientsID,
            "referring_ids"        : lint_tests.referring_ids,
            "value_range"         : lint_tests.allowed_values
            }
        

    def lint(self):
        """Run all lint tests."""
        passed = []
        warned = []
        failed = []

        # TOD progress bar
        for key, lint_test in self.lint_tests.items():
            self.logger.info("Running test %s", key)
            passed,warned,failed = lint_test(self.df, self.config,lint_test)
            self.passed.extend(passed)
            self.warned.extend(warned)
            self.failed.extend(failed)
        pass

    def _print_results(self, show_passed):
        """Print linting results to the command line.

        Uses the ``rich`` library to print a set of formatted tables to the command line
        summarising the linting results.
        """

        console = Console(force_terminal=True)

        # Spacing from log messages above
        console.print("")

        self.logger.info("Printing final results")

        # Helper function to format test links nicely
        @group()
        def format_result(test_results):
            # TODO
            """
            Given an list of error message IDs and the message texts, return a nicely formatted
            string for the terminal with appropriate ASCII colours.
            """
            for eid, msg in test_results:
                tools_version = __version__
                if "dev" in __version__:
                    tools_version = "latest"
                yield Markdown(
                    f"[{eid}](https://nf-co.re/tools/docs/{tools_version}/pipeline_lint_tests/{eid}.html): {msg}"
                )

        # Table of passed tests
        if len(self.passed) > 0 and show_passed:
            console.print(
                rich.panel.Panel(
                    format_result(self.passed),
                    title=rf"[bold][✔] {len(self.passed)} Pipeline Test{_s(self.passed)} Passed",
                    title_align="left",
                    style="green",
                    padding=1,
                )
            )

        # Table of warning tests
        if len(self.warned) > 0:
            console.print(
                rich.panel.Panel(
                    format_result(self.warned),
                    title=rf"[bold][!] {len(self.warned)} Pipeline Test Warning{_s(self.warned)}",
                    title_align="left",
                    style="yellow",
                    padding=1,
                )
            )

        # Table of failing tests
        if len(self.failed) > 0:
            console.print(
                rich.panel.Panel(
                    format_result(self.failed),
                    title=rf"[bold][✗] {len(self.failed)} Pipeline Test{_s(self.failed)} Failed",
                    title_align="left",
                    style="red",
                    padding=1,
                )
            )
