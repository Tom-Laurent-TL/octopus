"""
Utility functions for the Octopus CLI.
"""
import subprocess
import typer
from pathlib import Path


def find_project_root(start_dir: Path) -> tuple[Path | None, Path | None]:
    """
    Find the project root and app root by looking for pyproject.toml.
    
    Returns:
        tuple of (project_root, app_root) or (None, None) if not in an Octopus project
    """
    # Walk up from current directory looking for pyproject.toml
    project_root = start_dir
    while project_root.parent != project_root:  # Stop at filesystem root
        if (project_root / "pyproject.toml").exists():
            break
        project_root = project_root.parent
    
    # Verify we found it
    if not (project_root / "pyproject.toml").exists():
        return None, None
    
    # Find app root (should be project_root/app)
    app_root = project_root / "app"
    if not app_root.exists():
        return project_root, None
    
    return project_root, app_root


def run_command(cmd: list[str], cwd: Path = None) -> bool:
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error running command: {' '.join(cmd)}", err=True)
        typer.echo(f"   {e.stderr}", err=True)
        return False


def create_file(path: Path, content: str):
    """Create a file with the given content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        typer.echo(f"⚠️  Skipping existing file: {path}")
        return
    path.write_text(content, encoding="utf-8")
    typer.echo(f"📄 Created: {path}")
