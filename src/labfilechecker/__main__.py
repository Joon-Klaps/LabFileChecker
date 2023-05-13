import typer 

from lint import ExcelLint

def main(
        file:str,
        config:str = typer.Option("config sheet in [file]", help="Last name of person to greet."),
        ):
    """Run all lint tests."""
    lint = ExcelLint(config, file)
    lint.lint()
    lint.print_results()
    pass

if __name__ == "__main__":
    typer.run(main)