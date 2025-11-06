"""
Generator for Octopus Feature units.
"""
from pathlib import Path
from octopus_cli.utils import create_file
from octopus_cli.templates.templates import (
    get_feature_router_template,
    get_feature_service_template,
    get_feature_entities_template,
    get_feature_schemas_template,
    get_feature_readme_template,
    get_feature_todo_template,
)


def snake_to_pascal(name: str) -> str:
    """
    Convert snake_case to PascalCase.
    If name contains path separators, only converts the last segment.
    
    Examples:
        "user_profile" -> "UserProfile"
        "auth/permissions" -> "Permissions"
        "api/v1/users" -> "Users"
    """
    # Handle nested paths - take only the last segment
    if '/' in name or '\\' in name:
        name = name.replace('\\', '/').split('/')[-1]
    
    return ''.join(word.capitalize() for word in name.split('_'))


def _collect_available_shared_modules(features_dir: Path) -> dict:
    """
    Collect all shared modules available from the current scope.
    This includes shared modules at the current level and all parent levels.
    Handles duplicate module names at different depths by keeping all of them.
    
    Args:
        features_dir: The features/ directory where we're creating a feature
        
    Returns:
        dict mapping full_import_path to (shared_name, base_import_path)
        e.g., {
            "app.shared.auth": ("auth", "app"),
            "app.features.users.shared.auth": ("auth", "app.features.users")
        }
    """
    shared_modules = {}
    
    # Start from current level and build path components
    current_dir = features_dir.parent  # Go up from features/ to unit level
    path_stack = []
    
    # Walk up the directory tree until we hit the app root, building the path
    while current_dir.name != "app":
        # Check if we're in a feature (has a parent features/ directory)
        if current_dir.parent.name == "features":
            path_stack.insert(0, current_dir.name)  # Add feature name
            path_stack.insert(0, "features")  # Add features directory
            current_dir = current_dir.parent.parent  # Go up from feature to unit
        else:
            break  # Not in a nested feature structure
    
    # Now walk back down, collecting shared modules at each level
    current_dir = features_dir.parent  # Start again from unit level
    current_path = []
    
    # Re-traverse and collect shared modules
    temp_dir = features_dir.parent
    levels_to_check = []
    
    while temp_dir.name != "app":
        levels_to_check.insert(0, temp_dir)
        if temp_dir.parent.name == "features":
            temp_dir = temp_dir.parent.parent
        else:
            break
    
    # Always check app level
    app_root = features_dir
    while app_root.name != "app":
        app_root = app_root.parent
        if app_root.name == "app":
            break
    
    levels_to_check.insert(0, app_root)
    
    # Collect shared modules from each level
    # Use a list to preserve order and allow duplicates with different paths
    shared_modules_list = []
    
    for level_dir in levels_to_check:
        shared_dir = level_dir / "shared"
        
        if shared_dir.exists() and shared_dir.is_dir():
            # Build absolute path to this shared directory
            # Calculate path from app root to shared
            abs_path_parts = []
            temp = shared_dir
            while temp.name != "app":
                abs_path_parts.insert(0, temp.name)
                temp = temp.parent
            
            abs_path_parts.insert(0, "app")
            base_import_path = ".".join(abs_path_parts[:-1])  # Remove 'shared' from end
            
            # Find all shared modules at this level
            for item in shared_dir.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    shared_name = item.name
                    full_import_path = f"{base_import_path}.shared.{shared_name}"
                    
                    # Add all modules, even if same name at different depths
                    # Use full path as key to differentiate
                    shared_modules[full_import_path] = (shared_name, base_import_path)
    
    return shared_modules


def create_feature_unit(base_path: Path, feature_name: str):
    """
    Create an Octopus Feature unit with Service class pattern.
    Auto-imports all shared modules available from current scope (sibling and parent).
    
    Args:
        base_path: The features/ directory where the feature will be created
        feature_name: Name of the feature (snake_case)
    """
    feature_path = base_path / feature_name
    feature_path.mkdir(parents=True, exist_ok=True)
    
    # Convert feature name to PascalCase for class names
    class_name = snake_to_pascal(feature_name)
    
    # Collect all available shared modules from current scope and parent scopes
    shared_imports = _collect_available_shared_modules(base_path)
    
    # Create __init__.py with auto-imports from available shared modules
    init_content = '"""Feature module initialization."""\n'
    if shared_imports:
        # Sort by full path for consistent ordering
        for full_path in sorted(shared_imports.keys()):
            shared_name, base_import_path = shared_imports[full_path]
            init_content += f"\n# Auto-imported shared module: {shared_name}"
            # Add path hint if same module name exists at different depths
            if sum(1 for _, (name, _) in shared_imports.items() if name == shared_name) > 1:
                init_content += f" (from {base_import_path})"
            init_content += "\n"
            init_content += f"# from {base_import_path}.shared.{shared_name}.service import *\n"
            init_content += f"# from {base_import_path}.shared.{shared_name}.schemas import *\n"
    
    create_file(feature_path / "__init__.py", init_content)
    
    # Create router.py with service integration
    create_file(
        feature_path / "router.py",
        get_feature_router_template(feature_name, class_name)
    )
    
    # Create service.py with Service class
    create_file(
        feature_path / "service.py",
        get_feature_service_template(class_name, feature_name)
    )
    
    # Create entities.py
    create_file(
        feature_path / "entities.py",
        get_feature_entities_template(feature_name)
    )
    
    # Create schemas.py
    create_file(
        feature_path / "schemas.py",
        get_feature_schemas_template(class_name, feature_name)
    )
    
    # Create README.md
    create_file(
        feature_path / "README.md",
        get_feature_readme_template(class_name, feature_name)
    )
    
    # Create TODO.md
    create_file(
        feature_path / "TODO.md",
        get_feature_todo_template(class_name)
    )
    
    # Don't create empty subdirectories - they will be created when needed
    # by subsequent add feature/shared commands

