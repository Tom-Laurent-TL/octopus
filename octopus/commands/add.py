"""
Commands for adding features and shared modules to an Octopus application.
"""
import typer
from pathlib import Path

from octopus.utils import create_file, find_project_root
from octopus.generators.feature import create_feature_unit, snake_to_pascal
from octopus.generators.shared import create_shared_unit
from octopus.templates.templates import get_feature_test_template

app = typer.Typer(help="Commands for adding components to your Octopus application")

# Context variable to pass --crud flag from parent command to subcommands
_crud_context = {"enabled": False}


# Callback for add command to handle --crud flag
@app.callback(invoke_without_command=True)
def add_callback(
    ctx: typer.Context,
    crud: bool = typer.Option(False, "--crud", help="Generate with full CRUD implementation"),
):
    """Commands for adding components to your Octopus application"""
    # Store crud flag in context for subcommands to access
    _crud_context["enabled"] = crud
    
    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("feature")
def add_feature(
    name: str = typer.Argument(..., help="Name of the feature to add (use snake_case)"),
):
    """
    Add a new feature module to the application.
    
    Features are self-contained modules that implement specific functionality.
    Each feature follows the layered architecture pattern with a Service class.
    
    Use --crud to generate a fully-implemented CRUD feature with all endpoints.
    """
    crud = _crud_context["enabled"]
    typer.echo(f"🐙 Adding new {'CRUD ' if crud else ''}feature: {name}")
    
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
    
    # Detect context - find or create features/ directory
    features_dir = None
    
    # Handle nested feature paths (e.g., "conversations/messages")
    # Nested paths ALWAYS start from app/features/ (absolute from root)
    if '/' in name or '\\' in name:
        name = name.replace('\\', '/')
        parts = name.split('/')
        
        # Always start from app/features for nested paths
        if not (app_root / "features").exists():
            typer.echo(f"❌ Error: app/features/ directory does not exist.", err=True)
            raise typer.Exit(code=1)
        
        # Validate that parent feature exists
        potential_parent = app_root / "features" / parts[0]
        
        # Check if parent exists
        if not potential_parent.exists():
            typer.echo(f"❌ Error: Parent feature '{parts[0]}' does not exist.", err=True)
            typer.echo(f"   Expected at: {potential_parent}", err=True)
            typer.echo(f"   Create it first with: octopus add feature {parts[0]}", err=True)
            raise typer.Exit(code=1)
        
        # Check if parent is a valid feature (has router.py)
        if not (potential_parent / "router.py").exists():
            typer.echo(f"❌ Error: '{parts[0]}' exists but is not a feature (no router.py found).", err=True)
            typer.echo(f"   Path: {potential_parent}", err=True)
            raise typer.Exit(code=1)
        
        # Parent is valid - use its features/ subdirectory
        features_dir = potential_parent / "features"
        features_dir.mkdir(exist_ok=True)
        if not (features_dir / "__init__.py").exists():
            create_file(features_dir / "__init__.py", "")
        typer.echo(f"📁 Creating nested feature in: {parts[0]}/features/")
        
        # Update name to be just the remaining path
        name = '/'.join(parts[1:])
    
    # If not handled by nested path logic, use normal context detection
    if features_dir is None:
        # Check if we're already in a features/ directory
        if current_dir.name == "features":
            features_dir = current_dir
        # Check if current directory has features/ subdirectory
        elif (current_dir / "features").exists():
            features_dir = current_dir / "features"
        # Check if we're at project root and app/features exists
        elif current_dir == project_root and (app_root / "features").exists():
            features_dir = app_root / "features"
        # Check if current directory looks like a unit (has router.py or service.py)
        elif (current_dir / "router.py").exists() or (current_dir / "service.py").exists():
            # We're in a unit, create features/ directory here
            features_dir = current_dir / "features"
            features_dir.mkdir(exist_ok=True)
            create_file(features_dir / "__init__.py", "")
            typer.echo(f"📁 Created features/ directory in current unit")
        else:
            typer.echo("❌ Error: Not in an Octopus unit or project directory.", err=True)
            typer.echo("   Run this command from:", err=True)
            typer.echo("   - Project root (will use app/features/)", err=True)
            typer.echo("   - Inside a feature (will create features/ subdirectory)", err=True)
            typer.echo("   - Inside a features/ directory", err=True)
            raise typer.Exit(code=1)
    
    # Check if feature already exists
    feature_path = features_dir / name
    if feature_path.exists():
        typer.echo(f"⚠️  Feature '{name}' already exists at: {feature_path}", err=True)
        if not typer.confirm("Do you want to continue anyway?"):
            typer.echo("❌ Aborted.")
            raise typer.Exit(code=1)
    
    # Create the feature
    typer.echo(f"📁 Creating: {feature_path}/")
    
    if crud:
        typer.echo("⚠️  [PLACEHOLDER] CRUD generation not yet implemented")
        typer.echo("   Falling back to standard feature generation...")
        typer.echo("   Once implemented, this will generate full CRUD operations:")
        typer.echo("   - GET, POST, PUT, DELETE endpoints")
        typer.echo("   - Complete service methods (create, read, update, delete, list)")
        typer.echo("   - Entity model with id, created_at, updated_at")
        typer.echo("   - Create/Update/Response schemas")
        typer.echo("   - Pagination support")
    
    create_feature_unit(features_dir, name)
    
    class_name = snake_to_pascal(name)
    typer.echo(f"⚙️  Generated service class: {class_name}Service")
    
    # Create corresponding test and docs directories using validated project structure
    try:
        relative_from_app = feature_path.relative_to(app_root)
        # Create test structure mirroring the feature location
        tests_feature_path = project_root / "tests" / "app" / relative_from_app
        tests_feature_path.mkdir(parents=True, exist_ok=True)
        create_file(tests_feature_path / "__init__.py", "")
        create_file(
            tests_feature_path / "README.md",
            f"# Tests for {class_name}\n\nAdd tests for the {name} feature here.\n"
        )
        create_file(
            tests_feature_path / "TODO.md",
            f"# TODO - Tests for {class_name}\n\n- [ ] Write unit tests for {class_name}Service\n- [ ] Write integration tests for routes\n"
        )
        # Create actual test file
        feature_basename = name.split('/')[-1] if '/' in name else name
        create_file(
            tests_feature_path / f"test_{feature_basename}.py",
            get_feature_test_template(class_name, feature_basename)
        )
        typer.echo(f"📁 Created: {tests_feature_path}/")
        
        # Create docs structure mirroring the feature location
        docs_feature_path = project_root / "docs" / "app" / relative_from_app
        docs_feature_path.mkdir(parents=True, exist_ok=True)
        create_file(
            docs_feature_path / "README.md",
            f"# Documentation for {class_name}\n\nDocument the {name} feature here.\n"
        )
        create_file(
            docs_feature_path / "TODO.md",
            f"# TODO - Docs for {class_name}\n\n- [ ] Document API endpoints\n- [ ] Add usage examples\n"
        )
        typer.echo(f"📁 Created: {docs_feature_path}/")
    except ValueError:
        # Feature path is not under app/ - this shouldn't happen but handle gracefully
        typer.echo("⚠️  Skipping test/docs creation (feature not in app directory)")
    
    # Success message
    typer.echo(f"\n✅ Feature '{name}' added successfully! 🎉")
    typer.echo(f"\n� Location: {feature_path}")
    typer.echo(f"🔗 Endpoint: /{name}")
    typer.echo(f"\n💡 Next steps:")
    typer.echo(f"   1. Implement business logic in {class_name}Service")
    typer.echo(f"   2. Add API routes in router.py")
    typer.echo(f"   3. Define schemas in schemas.py")
    typer.echo(f"   4. Run your app and visit: http://localhost:8000/{name}")
    typer.echo(f"\n📝 Check {name}/TODO.md for more tasks!")


@app.command("shared")
def add_shared(
    name: str = typer.Argument(..., help="Name of the shared module to add (use snake_case)"),
):
    """
    Add a new shared module to the application.
    
    Shared modules contain reusable service logic, entities, and schemas
    that can be imported across features. They do not expose HTTP routes.
    
    Use --crud to generate a fully-implemented CRUD shared module.
    """
    crud = _crud_context["enabled"]
    typer.echo(f"🐙 Adding new {'CRUD ' if crud else ''}shared module: {name}")
    
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
    
    # Detect context - find or create shared/ directory
    shared_dir = None
    
    # Handle nested shared paths (e.g., "conversations/database")
    # Nested paths ALWAYS start from app/features/ (absolute from root)
    if '/' in name or '\\' in name:
        name = name.replace('\\', '/')
        parts = name.split('/')
        
        # Always start from app/features for nested paths
        if not (app_root / "features").exists():
            typer.echo(f"❌ Error: app/features/ directory does not exist.", err=True)
            raise typer.Exit(code=1)
        
        # Validate that parent feature exists
        potential_parent = app_root / "features" / parts[0]
        
        # Check if parent exists
        if not potential_parent.exists():
            typer.echo(f"❌ Error: Parent feature '{parts[0]}' does not exist.", err=True)
            typer.echo(f"   Expected at: {potential_parent}", err=True)
            typer.echo(f"   Create it first with: octopus add feature {parts[0]}", err=True)
            raise typer.Exit(code=1)
        
        # Check if parent is a valid feature (has router.py)
        if not (potential_parent / "router.py").exists():
            typer.echo(f"❌ Error: '{parts[0]}' exists but is not a feature (no router.py found).", err=True)
            typer.echo(f"   Path: {potential_parent}", err=True)
            raise typer.Exit(code=1)
        
        # Parent is valid - use its shared/ subdirectory
        shared_dir = potential_parent / "shared"
        shared_dir.mkdir(exist_ok=True)
        if not (shared_dir / "__init__.py").exists():
            create_file(shared_dir / "__init__.py", "")
        typer.echo(f"📁 Creating nested shared module in: {parts[0]}/shared/")
        
        # Update name to be just the remaining path
        name = '/'.join(parts[1:])
    
    # If not handled by nested path logic, use normal context detection
    if shared_dir is None:
        # Check if we're already in a shared/ directory
        if current_dir.name == "shared":
            shared_dir = current_dir
        # Check if current directory has shared/ subdirectory
        elif (current_dir / "shared").exists():
            shared_dir = current_dir / "shared"
        # Check if we're at project root and app/shared exists
        elif current_dir == project_root and (app_root / "shared").exists():
            shared_dir = app_root / "shared"
        # Check if current directory looks like a unit (has router.py, service.py, or features/)
        elif (current_dir / "router.py").exists() or (current_dir / "service.py").exists() or (current_dir / "features").exists():
            # We're in a unit, create shared/ directory here
            shared_dir = current_dir / "shared"
            shared_dir.mkdir(exist_ok=True)
            create_file(shared_dir / "__init__.py", "")
            typer.echo(f"📁 Created shared/ directory in current unit")
        else:
            typer.echo("❌ Error: Not in an Octopus unit or project directory.", err=True)
            typer.echo("   Run this command from:", err=True)
            typer.echo("   - Project root (will use app/shared/)", err=True)
            typer.echo("   - Inside a feature (will create shared/ subdirectory)", err=True)
            typer.echo("   - Inside a shared/ directory", err=True)
            raise typer.Exit(code=1)
    
    # Check if shared module already exists
    shared_path = shared_dir / name
    if shared_path.exists():
        typer.echo(f"⚠️  Shared module '{name}' already exists at: {shared_path}", err=True)
        if not typer.confirm("Do you want to continue anyway?"):
            typer.echo("❌ Aborted.")
            raise typer.Exit(code=1)
    
    # Create the shared module
    typer.echo(f"📁 Creating: {shared_path}/")
    
    if crud:
        typer.echo("⚠️  [PLACEHOLDER] CRUD generation not yet implemented")
        typer.echo("   Falling back to standard shared module generation...")
        typer.echo("   Once implemented, this will generate full CRUD service:")
        typer.echo("   - Complete CRUD methods (create, read, update, delete, list)")
        typer.echo("   - Entity model with id, created_at, updated_at")
        typer.echo("   - Create/Update/Response schemas")
        typer.echo("   - Repository pattern (optional)")
        typer.echo("   - Reusable across features (no HTTP routes)")
    
    class_name = create_shared_unit(shared_path, name)
    
    typer.echo(f"⚙️  Generated service class: {class_name}Service")
    typer.echo(f"📄 Created: service.py, entities.py, schemas.py")
    
    # Create corresponding test and docs directories using validated project structure
    try:
        relative_from_app = shared_path.relative_to(app_root)
        # Create test structure mirroring the shared module location
        tests_shared_path = project_root / "tests" / "app" / relative_from_app
        tests_shared_path.mkdir(parents=True, exist_ok=True)
        create_file(tests_shared_path / "__init__.py", "")
        create_file(
            tests_shared_path / "README.md",
            f"# Tests for {class_name}\n\nAdd tests for the {name} shared module here.\n"
        )
        create_file(
            tests_shared_path / "TODO.md",
            f"# TODO - Tests for {class_name}\n\n- [ ] Write unit tests for {class_name}Service\n- [ ] Test entity definitions\n- [ ] Validate schemas\n"
        )
        typer.echo(f"📁 Created: {tests_shared_path}/")
        
        # Create docs structure mirroring the shared module location
        docs_shared_path = project_root / "docs" / "app" / relative_from_app
        docs_shared_path.mkdir(parents=True, exist_ok=True)
        create_file(
            docs_shared_path / "README.md",
            f"# Documentation for {class_name}\n\nDocument the {name} shared module here.\n"
        )
        create_file(
            docs_shared_path / "TODO.md",
            f"# TODO - Docs for {class_name}\n\n- [ ] Document service methods\n- [ ] Add usage examples\n- [ ] Document entity schemas\n"
        )
        typer.echo(f"📁 Created: {docs_shared_path}/")
    except ValueError:
        # Shared path is not under app/ - this shouldn't happen but handle gracefully
        typer.echo("⚠️  Skipping test/docs creation (shared module not in app directory)")
    
    # Success message
    typer.echo(f"\n✅ Shared module '{name}' added successfully! 🎉")
    typer.echo(f"\n📍 Location: {shared_path}")
    typer.echo(f"🔗 Import in features:")
    typer.echo(f"   from app.shared.{name}.service import {class_name}Service")
    typer.echo(f"   from app.shared.{name}.entities import *")
    typer.echo(f"   from app.shared.{name}.schemas import *")
    typer.echo(f"\n� Next steps:")
    typer.echo(f"   1. Implement shared logic in {class_name}Service")
    typer.echo(f"   2. Define common entities in entities.py")
    typer.echo(f"   3. Define shared schemas in schemas.py")
    typer.echo(f"   4. Import in features as needed")
    typer.echo(f"\n📝 Check {name}/TODO.md for more tasks!")



