"""Module import and management utilities for tests."""

import sys
import os
import importlib
from typing import List, Any, Optional
from pathlib import Path


class ModuleManager:
    """Utility class for managing Python module imports in tests."""
    
    @staticmethod
    def ensure_parent_in_path(levels_up: int = 2) -> str:
        """
        Ensure parent directory is in Python path.
        
        Args:
            levels_up: Number of directory levels to go up from current file
            
        Returns:
            The path that was added
        """
        current_file = Path(__file__)
        parent_dir = current_file
        
        for _ in range(levels_up):
            parent_dir = parent_dir.parent
        
        parent_path = str(parent_dir.resolve())
        
        if parent_path not in sys.path:
            sys.path.insert(0, parent_path)
        
        return parent_path
    
    @staticmethod
    def reset_modules(*module_names: str) -> List[str]:
        """
        Remove modules from sys.modules to force reload.
        
        Args:
            *module_names: Names of modules to reset
            
        Returns:
            List of modules that were actually removed
        """
        removed = []
        
        for module_name in module_names:
            if module_name in sys.modules:
                del sys.modules[module_name]
                removed.append(module_name)
            
            # Also remove any submodules
            for key in list(sys.modules.keys()):
                if key.startswith(f"{module_name}."):
                    del sys.modules[key]
                    removed.append(key)
        
        return removed
    
    @staticmethod
    def import_with_env(module_name: str, **env_vars) -> Any:
        """
        Import a module with temporary environment variables.
        
        Args:
            module_name: Name of module to import
            **env_vars: Environment variables to set during import
            
        Returns:
            The imported module
        """
        from .env_manager import EnvironmentManager
        
        # Reset the module first
        ModuleManager.reset_modules(module_name)
        
        # Import with temporary environment
        with EnvironmentManager.temporary_env(**env_vars):
            return importlib.import_module(module_name)
    
    @staticmethod
    def replace_module(module_name: str, replacement: Any) -> Any:
        """
        Temporarily replace a module in sys.modules.
        
        Args:
            module_name: Name of module to replace
            replacement: The replacement module/object
            
        Returns:
            The original module (or None if it didn't exist)
        """
        original = sys.modules.get(module_name)
        sys.modules[module_name] = replacement
        return original
    
    @staticmethod
    def import_test_config() -> Any:
        """
        Import the test configuration module and replace the real config.
        
        This is specifically for PowerIt's test configuration.
        
        Returns:
            The test config module
        """
        # Ensure we can import from tests
        ModuleManager.ensure_parent_in_path()
        
        # Reset both config modules
        ModuleManager.reset_modules('config', 'tests.unit.test_config')
        
        # Import test config
        import tests.unit.test_config as test_config
        
        # Replace the real config with test config
        sys.modules['config'] = test_config
        
        return test_config
    
    @staticmethod
    def cleanup_imports(*prefixes: str) -> List[str]:
        """
        Remove all modules that start with given prefixes from sys.modules.
        
        Useful for cleaning up after tests that import many modules.
        
        Args:
            *prefixes: Module name prefixes to remove
            
        Returns:
            List of removed module names
        """
        removed = []
        
        for key in list(sys.modules.keys()):
            for prefix in prefixes:
                if key.startswith(prefix):
                    del sys.modules[key]
                    removed.append(key)
                    break
        
        return removed
    
    @staticmethod
    def get_module_path(module_name: str) -> Optional[Path]:
        """
        Get the file path of a module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Path to the module file, or None if not found
        """
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, '__file__') and module.__file__:
                return Path(module.__file__)
        except ImportError:
            pass
        
        return None
    
    @staticmethod
    def reload_module(module_name: str) -> Any:
        """
        Reload a module, ensuring all submodules are also reloaded.
        
        Args:
            module_name: Name of module to reload
            
        Returns:
            The reloaded module
        """
        # First, remove the module and all submodules
        ModuleManager.reset_modules(module_name)
        
        # Then import it fresh
        return importlib.import_module(module_name)