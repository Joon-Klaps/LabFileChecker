import typer 
import yaml

from lint import ExcelLint

def main(
        file:str,
        config:str = typer.Option("config sheet in [file]", help="configuration file used to check the excel file."),
        export_config:bool = typer.Option(False, help="save the configuration .yml file."),
        skiprows:int = typer.Option(1, help="Number of rows to skip at the beginning of the excel file."),
        ):
    """Run all lint tests."""
    lint = ExcelLint(config, file,skiprows)

    if export_config:
        with open ("config.yml","w", encoding="utf-8") as file:
            yaml.dump(lint.config,file)
    pass
    
    lint.lint()
    lint._print_results()

if __name__ == "__main__":
    typer.run(main)