"""
Generator for shared Octopus units.
"""
from pathlib import Path
from octopus.utils import create_file
from octopus.templates.templates import (
    get_shared_service_template,
    get_shared_entities_template,
    get_shared_schemas_template,
    get_shared_readme_template,
    get_shared_todo_template,
    get_readme_template,
    get_todo_template,
)


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('_'))


def create_shared_unit(shared_path: Path, shared_name: str):
    """
    Create a shared unit with service, entities, schemas.
    No router - shared modules are not HTTP-exposed.
    Auto-updates all sibling features to import this shared module.
    """
    class_name = snake_to_pascal(shared_name)
    
    # Create main shared files
    create_file(
        shared_path / "service.py",
        get_shared_service_template(class_name, shared_name)
    )
    
    create_file(
        shared_path / "entities.py",
        get_shared_entities_template(shared_name)
    )
    
    create_file(
        shared_path / "schemas.py",
        get_shared_schemas_template(class_name, shared_name)
    )
    
    create_file(
        shared_path / "README.md",
        get_shared_readme_template(class_name, shared_name)
    )
    
    create_file(
        shared_path / "TODO.md",
        get_shared_todo_template(class_name)
    )
    
    # Create __init__.py with exports for special modules
    if shared_name == "routing":
        init_content = """from .service import auto_discover_routers

__all__ = ["auto_discover_routers"]
"""
    elif shared_name == "config":
        init_content = """from .service import Settings, settings

__all__ = ["Settings", "settings"]
"""
    else:
        init_content = ""
    
    create_file(
        shared_path / "__init__.py",
        init_content
    )
    
    # Don't create empty subdirectories - they will be created when needed
    # by subsequent add feature/shared commands
    
    # Update sibling features to import this shared module (recursively)
    parent_dir = shared_path.parent  # Go up from shared/shared_name to shared/
    parent_parent = parent_dir.parent  # Go up to the unit level
    features_dir_path = parent_parent / "features"
    
    if features_dir_path.exists() and features_dir_path.is_dir():
        # Find all feature directories at the same level and recursively update
        # Pass the shared directory location for correct relative path calculation
        _update_features_recursively(features_dir_path, shared_name, parent_dir)
    
    return class_name


def _update_features_recursively(features_dir: Path, shared_name: str, shared_dir: Path):
    """Recursively update all features to import the shared module."""
    for feature_item in features_dir.iterdir():
        if feature_item.is_dir() and (feature_item / "__init__.py").exists():
            # Add import to this feature with correct relative path
            _add_shared_import_to_feature(feature_item, shared_name, shared_dir)
            
            # Recursively update nested features (pass same shared_dir)
            nested_features = feature_item / "features"
            if nested_features.exists() and nested_features.is_dir():
                _update_features_recursively(nested_features, shared_name, shared_dir)


def _add_shared_import_to_feature(feature_path: Path, shared_name: str, shared_dir: Path):
    """Add import statement for a shared module to a feature's __init__.py using absolute imports."""
    init_file = feature_path / "__init__.py"
    
    if not init_file.exists():
        return
    
    # Calculate absolute import path from app root to shared module
    # Build path from feature to app root, then to shared module
    abs_path_parts = []
    temp = shared_dir
    
    # Walk up from shared_dir to app root, collecting path components
    while temp.name != "app":
        abs_path_parts.insert(0, temp.name)
        temp = temp.parent
    
    abs_path_parts.insert(0, "app")
    absolute_path = ".".join(abs_path_parts)
    
    # Read existing content
    existing_content = init_file.read_text(encoding='utf-8')
    
    # Check if import already exists (check for full import path, not just name)
    full_import_line = f"# from {absolute_path}.shared.{shared_name}.service import *"
    if full_import_line in existing_content:
        return  # Already imported
    
    # Add the import with absolute path
    # Include path hint if same module name might exist at different depths
    new_imports = f"\n# Auto-imported shared module: {shared_name}"
    if absolute_path != "app":  # If not at app level, show where it's from
        new_imports += f" (from {absolute_path})"
    new_imports += "\n"
    new_imports += f"# from {absolute_path}.shared.{shared_name}.service import *\n"
    new_imports += f"# from {absolute_path}.shared.{shared_name}.schemas import *\n"
    
    # Insert after the docstring if it exists, or at the beginning
    if '"""' in existing_content:
        # Find the end of the docstring
        parts = existing_content.split('"""', 2)
        if len(parts) >= 3:
            updated_content = parts[0] + '"""' + parts[1] + '"""' + new_imports + parts[2]
        else:
            updated_content = existing_content + new_imports
    else:
        updated_content = existing_content + new_imports
    
    # Write back
    init_file.write_text(updated_content, encoding='utf-8')
