"""
Command for initializing new Octopus applications.
"""
import typer
from pathlib import Path

from octopus.utils import run_command, create_file
from octopus.generators.unit import create_octopus_unit
from octopus.generators.shared import create_shared_unit
from octopus.templates.templates import (
    get_main_template,
    get_env_example_template,
    get_root_readme_template,
    get_root_todo_template,
    get_tests_readme_template,
    get_tests_todo_template,
    get_docs_readme_template,
    get_docs_todo_template,
    get_architecture_doc_template,
    get_best_practices_doc_template,
    get_examples_doc_template,
    get_test_health_template,
    get_test_conftest_template,
)

app = typer.Typer(help="Initialize a new Octopus application")


@app.callback(invoke_without_command=True)
def init_command(
    ctx: typer.Context,
    path: str = typer.Option(".", help="Path where the app will be created"),
):
    """
    Initialize a new Octopus FastAPI application.
    
    Creates a fully structured, AI-friendly FastAPI project using the Octopus
    recursive fractal onion architecture.
    
    Examples:
        octopus init
        octopus init --path my_project
    """
    typer.echo("🐙 Creating Octopus app...")
    
    base_path = Path(path).resolve()
    
    # Check if we're in an empty directory or creating a new one
    if base_path.exists() and any(base_path.iterdir()):
        if not typer.confirm(f"⚠️  Directory {base_path} is not empty. Continue?"):
            typer.echo("❌ Aborted.")
            raise typer.Exit(code=1)
    
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Initialize with UV
    typer.echo("⚙️  Running: uv init --app")
    if not run_command(["uv", "init", "--app"], cwd=base_path):
        typer.echo("❌ Failed to initialize with uv")
        raise typer.Exit(code=1)
    
    # Step 2: Remove default main.py and README.md created by uv
    default_main = base_path / "main.py"
    if default_main.exists():
        typer.echo("🧹 Removing default main.py")
        default_main.unlink()
    
    default_readme = base_path / "README.md"
    if default_readme.exists():
        typer.echo("🧹 Removing default README.md")
        default_readme.unlink()
    
    # Step 3: Create virtual environment
    typer.echo("⚙️  Running: uv venv")
    if not run_command(["uv", "venv"], cwd=base_path):
        typer.echo("❌ Failed to create virtual environment")
        raise typer.Exit(code=1)
    
    # Step 4: Install dependencies
    typer.echo("⚙️  Installing dependencies...")
    dependencies = [
        (["uv", "add", "fastapi", "--extra", "standard"], "fastapi[standard]"),
        (["uv", "add", "pydantic"], "pydantic"),
        (["uv", "add", "pydantic-settings"], "pydantic-settings"),
        (["uv", "add", "--dev", "pytest"], "pytest (dev)"),
    ]
    
    for cmd, name in dependencies:
        typer.echo(f"   Installing {name}...")
        if not run_command(cmd, cwd=base_path):
            typer.echo(f"⚠️  Warning: Failed to install {name}")
    
    # Step 4.5: Add Octopus as optional dev dependency
    typer.echo("⚙️  Adding Octopus CLI as dev dependency...")
    octopus_cmd = ["uv", "add", "--optional", "dev", "octopus@git+https://github.com/Tom-Laurent-TL/octopus.git"]
    if not run_command(octopus_cmd, cwd=base_path):
        typer.echo("⚠️  Warning: Failed to add Octopus as dev dependency")
    else:
        typer.echo("   ✅ Added Octopus CLI to dev dependencies")
    
    # Step 5: Create directory structure
    typer.echo("📁 Creating Octopus structure...")
    
    app_path = base_path / "app"
    app_path.mkdir(exist_ok=True)
    
    # Create root app structure
    typer.echo("📁 Creating root app structure...")
    create_octopus_unit(app_path, is_root=True)
    
    # Create main.py
    typer.echo("📄 Creating main.py...")
    create_file(app_path / "main.py", get_main_template())
    
    # Create shared/config as a proper shared module
    typer.echo("📁 Creating default shared module: config")
    shared_dir = app_path / "shared"
    config_path = shared_dir / "config"
    create_shared_unit(config_path, "config")
    
    # Create shared/routing as a proper shared module (for auto-discovery)
    typer.echo("📁 Creating default shared module: routing")
    routing_path = shared_dir / "routing"
    create_shared_unit(routing_path, "routing")
    
    # Create .env.example
    typer.echo("📄 Creating .env.example...")
    create_file(base_path / ".env.example", get_env_example_template())

    # Create .env (copy from .env.example)
    typer.echo("📄 Creating .env from .env.example...")
    env_example_path = base_path / ".env.example"
    env_path = base_path / ".env"
    if env_example_path.exists():
        env_content = env_example_path.read_text()
        create_file(env_path, env_content)
    else:
        create_file(env_path, get_env_example_template())

    # Ensure .gitignore has entries for .pytest_cache/ and .env
    typer.echo("📄 Updating .gitignore...")
    gitignore_path = base_path / ".gitignore"
    pytest_cache_comment = "# Pytest cache (test runs)"
    pytest_cache_line = ".pytest_cache/"
    env_comment = "# Environment variables"
    env_line = ".env"
    gitignore_lines = []
    if gitignore_path.exists():
        lines = gitignore_path.read_text().splitlines()
        add_pytest = pytest_cache_line not in lines
        add_env = env_line not in lines
        if add_pytest and add_env:
            gitignore_lines.append(f"\n{pytest_cache_comment}\n{pytest_cache_line}\n\n{env_comment}\n{env_line}\n")
        elif add_pytest:
            gitignore_lines.append(f"\n{pytest_cache_comment}\n{pytest_cache_line}\n")
        elif add_env:
            gitignore_lines.append(f"\n{env_comment}\n{env_line}\n")
        if gitignore_lines:
            with gitignore_path.open("a", encoding="utf-8") as f:
                f.write("".join(gitignore_lines))
    else:
        create_file(gitignore_path, f"{pytest_cache_comment}\n{pytest_cache_line}\n\n{env_comment}\n{env_line}\n")
    
    # Create tests structure
    typer.echo("📁 Creating tests/ structure...")
    tests_path = base_path / "tests"
    tests_app_path = tests_path / "app"
    tests_app_path.mkdir(parents=True, exist_ok=True)
    
    create_file(tests_path / "__init__.py", "")
    create_file(tests_app_path / "__init__.py", "")
    create_file(tests_app_path / "README.md", get_tests_readme_template())
    create_file(tests_app_path / "TODO.md", get_tests_todo_template())
    
    # Create conftest.py with test fixtures
    create_file(tests_path / "conftest.py", get_test_conftest_template())
    
    # Create basic health/status tests
    create_file(tests_app_path / "test_health.py", get_test_health_template())
    
    (tests_app_path / "features").mkdir(exist_ok=True)
    (tests_app_path / "shared").mkdir(exist_ok=True)
    create_file(tests_app_path / "features" / "__init__.py", "")
    create_file(tests_app_path / "shared" / "__init__.py", "")
    
    # Create docs structure
    typer.echo("📁 Creating docs/ structure...")
    docs_path = base_path / "docs"
    docs_app_path = docs_path / "app"
    docs_app_path.mkdir(parents=True, exist_ok=True)
    
    create_file(docs_app_path / "README.md", get_docs_readme_template())
    create_file(docs_app_path / "TODO.md", get_docs_todo_template())
    
    (docs_app_path / "features").mkdir(exist_ok=True)
    (docs_app_path / "shared").mkdir(exist_ok=True)
    
    # Create comprehensive documentation
    typer.echo("📚 Creating documentation...")
    create_file(docs_path / "ARCHITECTURE.md", get_architecture_doc_template())
    create_file(docs_path / "BEST_PRACTICES.md", get_best_practices_doc_template())
    create_file(docs_path / "EXAMPLES.md", get_examples_doc_template())
    
    # Create root README.md and TODO.md
    create_file(base_path / "README.md", get_root_readme_template())
    create_file(base_path / "TODO.md", get_root_todo_template())
    
    # Success message
    typer.echo("\n✅ Done! Your Octopus app is ready 🎉")
    typer.echo(f"\n📂 Created at: {base_path}")
    typer.echo("\n🚀 Next steps:")
    typer.echo("   1. cd into your project directory")
    typer.echo("   2. Copy .env.example to .env and configure")
    typer.echo("   3. Run: uv run fastapi dev")
    typer.echo("   4. Visit: http://localhost:8000/docs")
    typer.echo("\n📖 Documentation:")
    typer.echo("   - docs/ARCHITECTURE.md - Architecture guide")
    typer.echo("   - docs/BEST_PRACTICES.md - Coding standards")
    typer.echo("   - docs/EXAMPLES.md - Real-world examples")
    typer.echo("\n📝 Check TODO.md for more tasks!")

