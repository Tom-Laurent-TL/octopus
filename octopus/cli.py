"""
Main entry point for the Octopus CLI.
"""
import typer
from octopus_cli.commands import add, remove, structure, init

app = typer.Typer(
    help="🐙 Octopus CLI – modular FastAPI architecture generator",
    add_completion=True,  # Enable shell completion
)

# Register subcommands
app.add_typer(init.app, name="init")
app.add_typer(add.app, name="add")
app.add_typer(remove.app, name="remove")
app.add_typer(structure.app, name="structure")

if __name__ == "__main__":
    app()
