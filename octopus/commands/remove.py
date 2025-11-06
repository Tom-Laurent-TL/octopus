"""
Commands for removing features and shared modules from an Octopus application.
"""
import typer
from pathlib import Path
import shutil

from octopus.utils import find_project_root
from rich.console import Console

app = typer.Typer(help="Commands for removing components from your Octopus application")
console = Console()

# Context variable to pass flags from parent command to subcommands
_context = {}


# Callback for remove command
@app.callback(invoke_without_command=True)
def remove_callback(ctx: typer.Context):
    """Commands for removing components from your Octopus application"""
    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("feature")
def remove_feature(
    name: str = typer.Argument(..., help="Name of the feature to remove (use snake_case)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Remove a feature module from the application.
    
    This will delete the feature directory and all its contents, including:
    - Feature files (router.py, service.py, entities.py, schemas.py, etc.)
    - Test files in tests/app/
    - Documentation files in docs/app/
    
    Examples:
        octopus remove feature users
        octopus remove feature auth/permissions  # Remove nested feature
        octopus remove feature users --force      # Skip confirmation
    """
    typer.echo(f"🐙 Removing feature: {name}")
    
    # Validate we're in an Octopus project first
    current_dir = Path.cwd()
    project_root, app_root = find_project_root(current_dir)
    
    if not project_root:
        typer.echo("❌ Error: Not in an Octopus project (no pyproject.toml found).", err=True)
        typer.echo("   Run 'octopus init' to create a new project first.", err=True)
        raise typer.Exit(code=1)
    
    if not app_root:
        typer.echo("❌ Error: No app/ directory found in project.", err=True)
        typer.echo(f"   Expected at: {project_root / 'app'}", err=True)
        raise typer.Exit(code=1)
    
    # Detect context - find the feature to remove
    feature_path = None
    
    # Handle nested feature paths (e.g., "conversations/messages")
    if '/' in name or '\\' in name:
        name = name.replace('\\', '/')
        parts = name.split('/')
        
        # Always start from app/features for nested paths
        if not (app_root / "features").exists():
            typer.echo(f"❌ Error: app/features/ directory does not exist.", err=True)
            raise typer.Exit(code=1)
        
        # Navigate to parent and find the feature
        # Build path segment by segment except the last one
        current_path = app_root / "features"
        for part in parts[:-1]:
            current_path = current_path / part
            if not current_path.exists():
                typer.echo(f"❌ Error: Parent feature '{part}' does not exist.", err=True)
                typer.echo(f"   Expected at: {current_path}", err=True)
                raise typer.Exit(code=1)
            # Check if it's a valid feature (has router.py)
            if not (current_path / "router.py").exists():
                typer.echo(f"❌ Error: '{part}' exists but is not a feature (no router.py found).", err=True)
                typer.echo(f"   Path: {current_path}", err=True)
                raise typer.Exit(code=1)
            # Move into the features subdirectory
            current_path = current_path / "features"
            if not current_path.exists():
                typer.echo(f"❌ Error: '{part}' has no features/ subdirectory.", err=True)
                typer.echo(f"   Expected at: {current_path}", err=True)
                raise typer.Exit(code=1)
        
        # Now add the final feature name
        feature_path = current_path / parts[-1]
    else:
        # Check if we're in a features/ directory
        if current_dir.name == "features":
            feature_path = current_dir / name
        # Check if current directory has features/ subdirectory
        elif (current_dir / "features").exists():
            feature_path = current_dir / "features" / name
        # Check if we're at project root and app/features exists
        elif current_dir == project_root and (app_root / "features").exists():
            feature_path = app_root / "features" / name
        # Check if current directory looks like a unit with features/
        elif (current_dir / "router.py").exists() and (current_dir / "features").exists():
            feature_path = current_dir / "features" / name
        else:
            typer.echo("❌ Error: Not in an Octopus unit or project directory.", err=True)
            typer.echo("   Run this command from:", err=True)
            typer.echo("   - Project root (will look in app/features/)", err=True)
            typer.echo("   - Inside a feature (will look in features/ subdirectory)", err=True)
            typer.echo("   - Inside a features/ directory", err=True)
            raise typer.Exit(code=1)
    
    # Check if feature exists
    if not feature_path.exists():
        typer.echo(f"❌ Error: Feature '{name}' does not exist at: {feature_path}", err=True)
        raise typer.Exit(code=1)
    
    # Check if it's actually a feature (has router.py)
    if not (feature_path / "router.py").exists():
        typer.echo(f"❌ Error: '{name}' exists but is not a feature (no router.py found).", err=True)
        typer.echo(f"   Path: {feature_path}", err=True)
        raise typer.Exit(code=1)
    
    # Confirm deletion
    if not force:
        console.print(f"\n[yellow]⚠️  This will delete:[/yellow]")
        console.print(f"   📁 {feature_path}")
        
        # Check for test and docs directories
        try:
            relative_from_app = feature_path.relative_to(app_root)
            tests_path = project_root / "tests" / "app" / relative_from_app
            docs_path = project_root / "docs" / "app" / relative_from_app
            
            if tests_path.exists():
                console.print(f"   🧪 {tests_path}")
            if docs_path.exists():
                console.print(f"   📚 {docs_path}")
        except ValueError:
            pass
        
        console.print()
        if not typer.confirm("❓ Are you sure you want to remove this feature?"):
            typer.echo("❌ Cancelled.")
            raise typer.Exit(code=0)
    
    # Remove the feature
    typer.echo(f"🗑️  Removing: {feature_path}/")
    shutil.rmtree(feature_path)
    
    # Clean up empty parent features/ directory if only __init__.py remains
    parent_features_dir = feature_path.parent
    if parent_features_dir.name == "features":
        remaining_items = list(parent_features_dir.iterdir())
        # Remove if empty or only contains __init__.py
        if len(remaining_items) == 0 or (len(remaining_items) == 1 and remaining_items[0].name == "__init__.py"):
            typer.echo(f"🧹 Cleaning up empty directory: {parent_features_dir}/")
            shutil.rmtree(parent_features_dir)
    
    # Remove corresponding test and docs directories
    try:
        relative_from_app = feature_path.relative_to(app_root)
        
        tests_path = project_root / "tests" / "app" / relative_from_app
        if tests_path.exists():
            typer.echo(f"🗑️  Removing: {tests_path}/")
            shutil.rmtree(tests_path)
        
        docs_path = project_root / "docs" / "app" / relative_from_app
        if docs_path.exists():
            typer.echo(f"🗑️  Removing: {docs_path}/")
            shutil.rmtree(docs_path)
    except ValueError:
        pass
    
    # Success message
    typer.echo(f"\n✅ Feature '{name}' removed successfully! 🎉")
    typer.echo(f"\n💡 Tip: Use 'git restore' to undo if this was a mistake")


@app.command("shared")
def remove_shared(
    name: str = typer.Argument(..., help="Name of the shared module to remove (use snake_case)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """
    Remove a shared module from the application.
    
    This will delete the shared module directory and all its contents, including:
    - Shared files (service.py, entities.py, schemas.py, etc.)
    - Test files in tests/app/
    - Documentation files in docs/app/
    
    Examples:
        octopus remove shared database
        octopus remove shared auth/permissions  # Remove nested shared
        octopus remove shared database --force   # Skip confirmation
    """
    typer.echo(f"🐙 Removing shared module: {name}")
    
    # Validate we're in an Octopus project first
    current_dir = Path.cwd()
    project_root, app_root = find_project_root(current_dir)
    
    if not project_root:
        typer.echo("❌ Error: Not in an Octopus project (no pyproject.toml found).", err=True)
        typer.echo("   Run 'octopus init' to create a new project first.", err=True)
        raise typer.Exit(code=1)
    
    if not app_root:
        typer.echo("❌ Error: No app/ directory found in project.", err=True)
        typer.echo(f"   Expected at: {project_root / 'app'}", err=True)
        raise typer.Exit(code=1)
    
    # Detect context - find the shared module to remove
    shared_path = None
    
    # Handle nested shared paths (e.g., "conversations/database")
    if '/' in name or '\\' in name:
        name = name.replace('\\', '/')
        parts = name.split('/')
        
        # Always start from app/features for nested paths
        if not (app_root / "features").exists():
            typer.echo(f"❌ Error: app/features/ directory does not exist.", err=True)
            raise typer.Exit(code=1)
        
        # Navigate to parent feature, drilling down through nested features
        # Build path segment by segment except the last one
        current_path = app_root / "features"
        for part in parts[:-1]:
            current_path = current_path / part
            if not current_path.exists():
                typer.echo(f"❌ Error: Parent feature '{part}' does not exist.", err=True)
                typer.echo(f"   Expected at: {current_path}", err=True)
                raise typer.Exit(code=1)
            # Check if it's a valid feature (has router.py)
            if not (current_path / "router.py").exists():
                typer.echo(f"❌ Error: '{part}' exists but is not a feature (no router.py found).", err=True)
                typer.echo(f"   Path: {current_path}", err=True)
                raise typer.Exit(code=1)
            # Move into the features subdirectory for next iteration
            current_path = current_path / "features"
            if not current_path.exists():
                typer.echo(f"❌ Error: '{part}' has no features/ subdirectory.", err=True)
                typer.echo(f"   Expected at: {current_path}", err=True)
                raise typer.Exit(code=1)
        
        # Now we're at the parent feature level, look in its shared/ directory
        # Go back up one level to the parent feature
        parent_feature = current_path.parent
        shared_path = parent_feature / "shared" / parts[-1]
    else:
        # Check if we're in a shared/ directory
        if current_dir.name == "shared":
            shared_path = current_dir / name
        # Check if current directory has shared/ subdirectory
        elif (current_dir / "shared").exists():
            shared_path = current_dir / "shared" / name
        # Check if we're at project root and app/shared exists
        elif current_dir == project_root and (app_root / "shared").exists():
            shared_path = app_root / "shared" / name
        # Check if current directory looks like a unit with shared/
        elif ((current_dir / "router.py").exists() or (current_dir / "features").exists()) and (current_dir / "shared").exists():
            shared_path = current_dir / "shared" / name
        else:
            typer.echo("❌ Error: Not in an Octopus unit or project directory.", err=True)
            typer.echo("   Run this command from:", err=True)
            typer.echo("   - Project root (will look in app/shared/)", err=True)
            typer.echo("   - Inside a feature (will look in shared/ subdirectory)", err=True)
            typer.echo("   - Inside a shared/ directory", err=True)
            raise typer.Exit(code=1)
    
    # Check if shared module exists
    if not shared_path.exists():
        typer.echo(f"❌ Error: Shared module '{name}' does not exist at: {shared_path}", err=True)
        raise typer.Exit(code=1)
    
    # Check if it's actually a shared module (has service.py)
    if not (shared_path / "service.py").exists():
        typer.echo(f"❌ Error: '{name}' exists but is not a shared module (no service.py found).", err=True)
        typer.echo(f"   Path: {shared_path}", err=True)
        raise typer.Exit(code=1)
    
    # Confirm deletion
    if not force:
        console.print(f"\n[yellow]⚠️  This will delete:[/yellow]")
        console.print(f"   📁 {shared_path}")
        
        # Check for test and docs directories
        try:
            relative_from_app = shared_path.relative_to(app_root)
            tests_path = project_root / "tests" / "app" / relative_from_app
            docs_path = project_root / "docs" / "app" / relative_from_app
            
            if tests_path.exists():
                console.print(f"   🧪 {tests_path}")
            if docs_path.exists():
                console.print(f"   📚 {docs_path}")
        except ValueError:
            pass
        
        console.print()
        if not typer.confirm("❓ Are you sure you want to remove this shared module?"):
            typer.echo("❌ Cancelled.")
            raise typer.Exit(code=0)
    
    # Remove the shared module
    typer.echo(f"🗑️  Removing: {shared_path}/")
    shutil.rmtree(shared_path)
    
    # Clean up empty parent shared/ directory if only __init__.py remains
    parent_shared_dir = shared_path.parent
    if parent_shared_dir.name == "shared":
        remaining_items = list(parent_shared_dir.iterdir())
        # Remove if empty or only contains __init__.py
        if len(remaining_items) == 0 or (len(remaining_items) == 1 and remaining_items[0].name == "__init__.py"):
            typer.echo(f"🧹 Cleaning up empty directory: {parent_shared_dir}/")
            shutil.rmtree(parent_shared_dir)
    
    # Remove corresponding test and docs directories
    try:
        relative_from_app = shared_path.relative_to(app_root)
        
        tests_path = project_root / "tests" / "app" / relative_from_app
        if tests_path.exists():
            typer.echo(f"🗑️  Removing: {tests_path}/")
            shutil.rmtree(tests_path)
        
        docs_path = project_root / "docs" / "app" / relative_from_app
        if docs_path.exists():
            typer.echo(f"🗑️  Removing: {docs_path}/")
            shutil.rmtree(docs_path)
    except ValueError:
        pass
    
    # Success message
    typer.echo(f"\n✅ Shared module '{name}' removed successfully! 🎉")
    typer.echo(f"\n💡 Tip: Use 'git restore' to undo if this was a mistake")
