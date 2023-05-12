#!/usr/env python
"""My main script to check for inconsistencies in lab (excel) files."""

import typer
import pandas as pd

app = typer.Typer()

@app.command()
def main(title:str = typer.Option(..., prompt=True)):
    print (title)

if __name__ == "__main__":
    typer.run(main)