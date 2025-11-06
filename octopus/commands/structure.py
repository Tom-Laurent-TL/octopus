"""
Commands for displaying and analyzing project structure.
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text

from octopus_cli.utils import find_project_root

app = typer.Typer(help="Commands for viewing project structure")
console = Console()


def _is_octopus_unit(path: Path) -> tuple[bool, str]:
    """Check if a directory is an Octopus unit (feature or shared module)."""
    if not path.is_dir():
        return False, ""
    
    has_router = (path / "router.py").exists()
    has_service = (path / "service.py").exists()
    has_init = (path / "__init__.py").exists()
    
    if has_router and has_service:
        return True, "feature"
    elif has_service and has_init and not has_router:
        return True, "shared"
    
    return False, ""


def _extract_routes(router_path: Path) -> list[str]:
    """Extract route definitions from a router.py file."""
    routes = []
    try:
        content = router_path.read_text(encoding="utf-8")
        import re
        
        # Match @router.get("/path"), @router.post("/path"), etc.
        pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            routes.append(f"{method} {path}")
        
    except Exception:
        pass
    
    return routes


def _should_skip(path: Path, name: str) -> bool:
    """Check if a path should be skipped."""
    skip_names = {
        '__pycache__', '.pytest_cache', '.git', '.venv', 'venv',
        'node_modules', '.idea', '.vscode', '*.pyc', '.DS_Store',
        'dist', 'build', '*.egg-info',
        'tests', 'docs'  # Skip tests and docs as they mirror app structure
    }
    
    return name in skip_names or name.startswith('.')


def _build_tree(path: Path, tree: Tree, max_depth: int, current_depth: int = 0, show_files: bool = True, parent_type: str = "") -> dict:
    """Recursively build the tree structure and collect stats."""
    stats = {
        "features": 0,
        "shared": 0,
        "routers": 0,
        "services": 0,
        "total_files": 0,
        "total_dirs": 0,
    }
    
    if current_depth >= max_depth:
        return stats
    
    try:
        items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    except PermissionError:
        tree.add("❌ [red]Permission denied[/red]")
        return stats
    
    for item in items:
        if _should_skip(item, item.name):
            continue
        
        if item.is_dir():
            stats["total_dirs"] += 1
            
            # Check for special directories first (before unit detection)
            if item.name == "app":
                # Special emoji for the main app directory
                branch = tree.add(f"🏠 {item.name}/", style="bold blue")
                
                dir_stats = _build_tree(item, branch, max_depth, current_depth + 1, show_files)
                for key in stats:
                    stats[key] += dir_stats[key]
            
            elif item.name in ["features", "shared"]:
                # Skip the features/ and shared/ container directories
                # Instead, directly show their contents at the current level
                dir_stats = _build_tree(item, tree, max_depth, current_depth, show_files, item.name)
                for key in stats:
                    stats[key] += dir_stats[key]
            
            else:
                # Check if it's an Octopus unit
                is_unit, unit_type = _is_octopus_unit(item)
                
                if is_unit:
                    if unit_type == "feature":
                        stats["features"] += 1
                        icon = "⚡"
                        style = "bold cyan"
                        
                        # Extract routes from router.py
                        router_file = item / "router.py"
                        routes = _extract_routes(router_file) if router_file.exists() else []
                        
                        if routes:
                            route_info = f" ({len(routes)} route{'s' if len(routes) != 1 else ''})"
                            branch = tree.add(f"{icon} {item.name}/{route_info}", style=style)
                            
                            # Add routes as sub-items
                            for route in routes:
                                method, path = route.split(" ", 1)
                                method_colors = {
                                    "GET": "green",
                                    "POST": "blue",
                                    "PUT": "yellow",
                                    "DELETE": "red",
                                    "PATCH": "magenta"
                                }
                                color = method_colors.get(method, "white")
                                branch.add(f"[{color}]{method}[/{color}] [dim]{path}[/dim]")
                        else:
                            branch = tree.add(f"{icon} {item.name}/", style=style)
                        
                    elif unit_type == "shared":
                        stats["shared"] += 1
                        icon = "📦"
                        style = "bold yellow"
                        branch = tree.add(f"{icon} {item.name}/", style=style)
                    
                    # Show unit contents
                    unit_stats = _build_tree(item, branch, max_depth, current_depth + 1, show_files, unit_type)
                    for key in stats:
                        stats[key] += unit_stats[key]
                
                else:
                    # Regular directory
                    branch = tree.add(f"� {item.name}/", style="blue")
                    
                    dir_stats = _build_tree(item, branch, max_depth, current_depth + 1, show_files)
                    for key in stats:
                        stats[key] += dir_stats[key]
        
        elif item.is_file():
            # Count files even if not showing them
            stats["total_files"] += 1
            
            name = item.name
            if name == "router.py":
                stats["routers"] += 1
            elif name == "service.py":
                stats["services"] += 1
            
            # Only add to tree if show_files is True
            if show_files:
                # Determine file type and icon
                suffix = item.suffix
                
                if name == "router.py":
                    icon = "🛣️"
                    style = "green"
                elif name == "service.py":
                    icon = "⚙️"
                    style = "yellow"
                elif name == "main.py":
                    icon = "🚀"
                    style = "bold green"
                elif name == "__init__.py":
                    icon = "📄"
                    style = "dim"
                elif suffix == ".py":
                    icon = "🐍"
                    style = "white"
                elif name == "pyproject.toml":
                    icon = "📋"
                    style = "bold blue"
                elif name in ["README.md", "TODO.md"]:
                    icon = "📖"
                    style = "cyan"
                elif suffix in [".md", ".rst", ".txt"]:
                    icon = "📝"
                    style = "white"
                elif suffix in [".json", ".yaml", ".yml", ".toml"]:
                    icon = "⚙️"
                    style = "magenta"
                else:
                    icon = "📄"
                    style = "white"
                
                tree.add(f"{icon} {name}", style=style)
    
    return stats


@app.callback(invoke_without_command=True)
def show_structure(
    ctx: typer.Context,
    path: str = typer.Option(None, help="Path to the project to analyze (defaults to project root)"),
    depth: int = typer.Option(4, help="Maximum depth to display"),
    show_files: bool = typer.Option(False, "--files", help="Show files in addition to directories"),
):
    """
    Display the structure of an Octopus application.
    
    Shows the directory tree and organization of the project with:
    - 🎯 Features (with routers)
    - 📦 Shared modules (reusable services)
    - 🛣️ Routers and ⚙️ Services
    - File type indicators
    
    By default, only shows directories. Use --files to include files.
    Note: tests/ and docs/ are hidden as they mirror the app/ structure.
    """
    # If no path specified, use find_project_root to locate the project
    if path is None:
        current_dir = Path.cwd()
        project_root, app_root = find_project_root(current_dir)
        
        if not project_root:
            console.print("[red]❌ Error: Not in an Octopus project (no pyproject.toml found).[/red]")
            console.print("[yellow]   Run 'octopus create app' to create a new project first.[/yellow]")
            console.print("[yellow]   Or specify a path with --path[/yellow]")
            raise typer.Exit(code=1)
        
        project_path = project_root
        console.print(f"[dim]📍 Found project at: {project_path}[/dim]\n")
    else:
        project_path = Path(path).resolve()
        
        if not project_path.exists():
            console.print(f"[red]❌ Error: Path does not exist: {project_path}[/red]")
            raise typer.Exit(code=1)
        
        if not project_path.is_dir():
            console.print(f"[red]❌ Error: Path is not a directory: {project_path}[/red]")
            raise typer.Exit(code=1)
    
    # Check if it's an Octopus project
    is_octopus = (project_path / "pyproject.toml").exists()
    has_app = (project_path / "app").exists()
    
    # Create the tree
    tree = Tree(
        f"🐙 [bold magenta]{project_path.name}/[/bold magenta]",
        guide_style="dim"
    )
    
    stats = _build_tree(project_path, tree, depth, 0, show_files)
    
    # Display the tree in a panel
    console.print()
    console.print(Panel(tree, title="[bold cyan]Project Structure[/bold cyan]", border_style="cyan", padding=(1, 2)))
    
    # Display statistics
    if is_octopus and has_app:
        stats_text = Text()
        stats_text.append("📊 Statistics: ", style="bold")
        stats_text.append(f"{stats['features']} features", style="cyan")
        stats_text.append(" • ", style="dim")
        stats_text.append(f"{stats['shared']} shared modules", style="yellow")
        stats_text.append(" • ", style="dim")
        stats_text.append(f"{stats['routers']} routers", style="green")
        stats_text.append(" • ", style="dim")
        stats_text.append(f"{stats['services']} services", style="yellow")
        
        if show_files:
            stats_text.append(" • ", style="dim")
            stats_text.append(f"{stats['total_files']} files", style="white")
        
        console.print(Panel(stats_text, border_style="blue"))
    else:
        if not is_octopus:
            console.print("[yellow]⚠️  Not an Octopus project (no pyproject.toml found)[/yellow]")
        elif not has_app:
            console.print("[yellow]⚠️  No app/ directory found[/yellow]")
    
    console.print()

