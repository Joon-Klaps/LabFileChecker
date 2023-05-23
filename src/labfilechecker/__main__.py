import typer 
from typing import Optional
from rich.panel import Panel
from rich.console import Console
import yaml
import os 
import requests

import labfilechecker
from .lint import ExcelLint
app = typer.Typer(add_completion=False)

def version_callback(value: bool):
    if value:
        print(f"labfilechecker Version: {labfilechecker.__version__}")
        raise typer.Exit()

def version_check(curr_version):
    """Checks for a newer version of labfilechecker"""
    try:
        response = requests.get("https://api.github.com/repos/Joon-Klaps/LabFileChecker/releases/latest")
        response.raise_for_status()
        latest_version = response.json()["name"]
        if latest_version != curr_version:
            console = Console(force_terminal=True)
            console.print(
                Panel(
                    f"labfilechecker {curr_version} is not the latest version, you should upgrade to {latest_version} \n\n Use:\tpip install --upgrade https://github.com/Joon-Klaps/LabFileChecker/archive/refs/heads/master.zip ",
                    title="Upgrade Available",
                    style="bold dark_orange",
                )
            )
    except requests.exceptions.ConnectionError:
        pass

    # If the request fails, do nothing
    except requests.exceptions.HTTPError:
        pass
    
    except requests.exceptions.RequestException:
        pass

@app.command()
def main(
        file:str,
        report: Optional[str] = typer.Option("report.xlsx", help="save the linting results to a excel file."),
        export_report: Optional[bool] = typer.Option(True, help="save the linting results to a excel file."),
        config:Optional[str] = typer.Option("config sheet in [file]", help="configuration file used to check the excel file."),
        export_config:Optional[bool] = typer.Option(False, help="save the configuration .yml file."),
        skiprows:Optional[int] = typer.Option(0, help="Number of rows to skip at the beginning of the excel file."),
        version: Optional[bool] = typer.Option(None, "--version", callback=version_callback)

        ):
    """Run all lint tests."""

    print(f"labfilechecker Version: {labfilechecker.__version__}")
    version_check(labfilechecker.__version__)

    if not os.path.isfile(file):
        raise typer.Exit(f"{file} does not exist.")

    lint = ExcelLint(config, file,skiprows,report)

    if export_config:
        with open ("config.yml","w", encoding="utf-8") as file:
            yaml.dump(lint.config,file)
    pass

    lint.lint()

    if export_report:
        lint._save_results()
    
    lint._print_results()
        



