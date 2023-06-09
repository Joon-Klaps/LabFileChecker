#!/usr/env python
"""My main script to check for inconsistencies in lab (excel) files."""

import time
import rich
import rich.progress
from rich.console import Console
from rich.columns import Columns
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, BarColumn
from rich.table import Table
import pandas as pd

from .extract_config import extract_config
from .lint_tests import *

class ExcelLint:
    """Class to check for inconsistencies in lab (excel) files."""
    
    def __init__(self, config:str, file:str,skip_tests:list, skip_rows:int, report:str, ):
        """Initialize the class."""        

        self.config = extract_config(config)
        self.skip_rows = skip_rows
        self.report = report

        df = pd.read_excel(file, skiprows=self.skip_rows, na_values=['NA','na','N/A','n/a','nan','NaN','NAN'], keep_default_na=False)
        df  = df.reset_index().rename(columns={'index': 'Row_Number'})
        df['Row_Number'] = df['Row_Number'] + self.skip_rows +2 
        self.df = df
        
        self.lint_tests = {
            "column_names"        : column_names,
            "duplicate_samples"   : duplicate_samples,
            "dates"               : dates,
            "unrealistic_dates"   : unrealistic_dates,
            "numeric_values"      : numeric_values,
            "presence_databaseID" : presence_databaseID,
            "referring_ids"       : referring_ids,
            "allowed_values"      : allowed_values,
            "presence_value"     : presence_value
            }
        self.passed = []
        self.warned = []
        self.failed = []
        self.skipped = []
        if skip_tests:
            skipped = [ LintResult(None, None, test, test,f"skipping {test}") for test in skip_tests]
            self.skipped.extend(skipped)

            # Remove skipped tests from lint_tests
            self.lint_tests = {key: value for key, value in self.lint_tests.items() if key not in skip_tests}

    def lint(self):
        """Run all lint tests."""
        passed = []
        warned = []
        failed = []


        # Create a Progress instance with the desired format
        progress = Progress("[progress.description]{task.description}", BarColumn())
        df_noBlanks = self.df.copy().replace(to_replace = ['',' ','  '], value = pd.NA)
        with progress:
            # Define a task for the progress bar
            task = progress.add_task("[cyan]Running tests...", total=len(self.lint_tests))

            for key, lint_test in self.lint_tests.items():
                # Update the task description for each test
                try :   
                    progress.update(task, description=f"Running test {key}")

                    passed, warned, failed = lint_test(df_noBlanks if key != "presence_value" else self.df.copy(), self.config)
                    self.passed.extend(passed)
                    self.warned.extend(warned)
                    self.failed.extend(failed)
                    
                    time.sleep(0.1)
                except KeyError as error:
                    self.skipped.extend([LintResult(None, None, key, key,f"KeyError: {error} \n\n !! Check your files, skipping test {key} !!")])
                # Advance the progress bar for each test
                progress.advance(task)

        # Mark the task as completed
        progress.stop()

    def _save_results(self):
        """Save linting to a excel file."""

        def lint_result_to_df(lint_result_list):
            """Convert a list of lint test results into a pandas dataframe."""
            lint_results = [{
                    'checked' :"",
                    'row': result.row,
                    'column': result.column,
                    'value': result.value,
                    'lint_test': result.lint_test,
                    'message': result.message
                } for result in lint_result_list]
            df = pd.DataFrame(lint_results)
            return df

        with pd.ExcelWriter(self.report, mode = 'w') as excel_writer:
            if len(self.warned) > 0:
                df = lint_result_to_df(self.warned)
                df.to_excel(excel_writer,sheet_name='Warnings',index=False)

            if len(self.failed) > 0:
                df = lint_result_to_df(self.failed)
                df.to_excel(excel_writer,sheet_name='Failed',index=False)    
            
            if len(self.passed) > 0:
                df = lint_result_to_df(self.passed)
                df.to_excel(excel_writer,sheet_name='Passed',index=False)

            if len(self.skipped) > 0:
                df = lint_result_to_df(self.skipped)
                df.to_excel(excel_writer,sheet_name='skipped',index=False)            


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
        
        # Table of skipped tests
        if len(self.skipped) > 0:
            console.print(
                rich.panel.Panel(
                    format_result(self.skipped, "magenta"),
                    title=rf"[bold][>>] {len(self.passed)} Tests skipped",
                    title_align="left",
                    style="magenta",
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
        
        summary_table = Table(show_header=True, header_style="bold blue", style="blue")
        summary_table.add_column("Passed")
        summary_table.add_column("Warned")
        summary_table.add_column("Failed")
        summary_table.add_column("skipped")
        summary_table.add_row(
            str(len(self.passed)),
            str(len(self.warned)),
            str(len(self.failed)),
            str(len(self.skipped))
        )
        if len(self.warned) + len(self.failed) == 0:
            success_message = Text("😎 All tests passed! 🎉🎉🎉", style="bold")
            panel_content = Columns([summary_table, success_message], align="center",width=40)
        else:
            panel_content = summary_table

        summary_panel = Panel(
            panel_content,
            title="[bold]Summary",
            title_align="left",
            style="blue",
            padding=1,
        )

        console.print(
            summary_panel
        )   
