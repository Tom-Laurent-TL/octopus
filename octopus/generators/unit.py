"""
Generator for Octopus Units.
"""
from pathlib import Path
from octopus.utils import create_file
from octopus.templates.templates import (
    get_root_router_template,
    get_router_template,
    get_service_template,
    get_entities_template,
    get_schemas_template,
    get_readme_template,
    get_todo_template,
)


def create_octopus_unit(base_path: Path, unit_name: str = None, is_root: bool = False):
    """
    Create an Octopus Unit structure with router, service, entities, schemas,
    and recursive features/shared subdirectories.
    
    Args:
        base_path: The base directory where the unit will be created
        unit_name: Name of the unit (None for root)
        is_root: Whether this is the root app unit
    """
    unit_path = base_path if is_root else base_path / unit_name
    unit_path.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py with imports for root app
    if is_root:
        init_content = """# Import shared modules to make them available throughout the app
from app.shared.config import settings
from app.shared.routing import auto_discover_routers

__all__ = ["settings", "auto_discover_routers"]
"""
    else:
        init_content = ""
    
    create_file(unit_path / "__init__.py", init_content)
    
    # Create router.py
    if is_root:
        router_content = get_root_router_template()
    else:
        router_content = get_router_template()
    create_file(unit_path / "router.py", router_content)
    
    # Create service.py
    create_file(unit_path / "service.py", get_service_template())
    
    # Create entities.py
    create_file(unit_path / "entities.py", get_entities_template())
    
    # Create schemas.py
    create_file(unit_path / "schemas.py", get_schemas_template())
    
    # Create README.md and TODO.md
    # Root app gets special content, non-root units get standard content
    if is_root:
        readme_content = """# App Module

This is the root application module following the Octopus architecture.

## Structure

- `main.py` - FastAPI application entry point
- `router.py` - Root router with auto-discovery
- `__init__.py` - Exports shared utilities (settings, auto_discover_routers)
- `features/` - Feature modules (add with `octopus add feature <name>`)
- `shared/` - Shared utilities (add with `octopus add shared <name>`)

## Default Shared Modules

- `shared/config/` - Application settings using pydantic-settings
- `shared/routing/` - Router auto-discovery utilities

## Adding Components

```bash
# Add a feature
octopus add feature users

# Add a shared module
octopus add shared database

# View structure
octopus structure
```

Each feature and shared module is a self-contained unit with its own:
- router.py (features only)
- service.py
- entities.py
- schemas.py
- features/ subdirectory (recursive)
- shared/ subdirectory (recursive)
"""
        todo_content = """# TODO - App Module

- [ ] Add your first feature with `octopus add feature <name>`
- [ ] Configure shared/config with your settings
- [ ] Implement business logic in service layers
- [ ] Define domain models in entities
- [ ] Create API schemas in schemas
"""
        create_file(unit_path / "README.md", readme_content)
        create_file(unit_path / "TODO.md", todo_content)
    else:
        create_file(unit_path / "README.md", get_readme_template(unit_name))
        create_file(unit_path / "TODO.md", get_todo_template(unit_name))
    
    # Create recursive subdirectories
    features_path = unit_path / "features"
    shared_path = unit_path / "shared"
    
    features_path.mkdir(exist_ok=True)
    shared_path.mkdir(exist_ok=True)
    
    create_file(features_path / "__init__.py", "")
    create_file(shared_path / "__init__.py", "")

