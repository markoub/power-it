"""Environment variable management utilities for tests."""

import os
from contextlib import contextmanager
from typing import Dict, Optional, List, Any


class EnvironmentManager:
    """Utility class for managing environment variables in tests."""
    
    @staticmethod
    @contextmanager
    def temporary_env(**kwargs):
        """
        Context manager for temporarily setting environment variables.
        
        Example:
            with EnvironmentManager.temporary_env(POWERIT_OFFLINE="1", API_KEY="test"):
                # Environment variables are set here
                pass
            # Original values are restored here
        
        Args:
            **kwargs: Environment variables to set (None values will unset the variable)
        """
        original_values = {}
        
        # Save original values and set new ones
        for key, value in kwargs.items():
            original_values[key] = os.environ.get(key)
            
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)
        
        try:
            yield
        finally:
            # Restore original values
            for key, original_value in original_values.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
    
    @staticmethod
    def save_env_state(*keys: str) -> Dict[str, Optional[str]]:
        """
        Save the current state of specified environment variables.
        
        Args:
            *keys: Environment variable names to save
            
        Returns:
            Dictionary mapping variable names to their current values
        """
        return {key: os.environ.get(key) for key in keys}
    
    @staticmethod
    def restore_env_state(state: Dict[str, Optional[str]]) -> None:
        """
        Restore environment variables to a previously saved state.
        
        Args:
            state: Dictionary mapping variable names to their values
        """
        for key, value in state.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    
    @staticmethod
    @contextmanager
    def clean_env(*keys: str):
        """
        Context manager that temporarily removes specified environment variables.
        
        Example:
            with EnvironmentManager.clean_env("API_KEY", "SECRET"):
                # API_KEY and SECRET are not in environment here
                pass
            # Original values are restored here
        
        Args:
            *keys: Environment variable names to temporarily remove
        """
        saved_state = EnvironmentManager.save_env_state(*keys)
        
        # Remove the variables
        for key in keys:
            os.environ.pop(key, None)
        
        try:
            yield
        finally:
            # Restore original state
            EnvironmentManager.restore_env_state(saved_state)
    
    @staticmethod
    def get_bool_env(key: str, default: bool = False) -> bool:
        """
        Get a boolean value from an environment variable.
        
        Recognizes: '1', 'true', 'yes', 'on' as True (case-insensitive)
        
        Args:
            key: Environment variable name
            default: Default value if variable is not set
            
        Returns:
            Boolean value
        """
        value = os.environ.get(key, "").lower()
        if not value:
            return default
        
        return value in ("1", "true", "yes", "on")
    
    @staticmethod
    def get_int_env(key: str, default: int = 0) -> int:
        """
        Get an integer value from an environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if variable is not set or invalid
            
        Returns:
            Integer value
        """
        try:
            return int(os.environ.get(key, default))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_float_env(key: str, default: float = 0.0) -> float:
        """
        Get a float value from an environment variable.
        
        Args:
            key: Environment variable name
            default: Default value if variable is not set or invalid
            
        Returns:
            Float value
        """
        try:
            return float(os.environ.get(key, default))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_list_env(key: str, separator: str = ",", default: Optional[List[str]] = None) -> List[str]:
        """
        Get a list value from an environment variable.
        
        Args:
            key: Environment variable name
            separator: String to split on
            default: Default value if variable is not set
            
        Returns:
            List of strings
        """
        value = os.environ.get(key, "")
        if not value:
            return default or []
        
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    @staticmethod
    @contextmanager
    def mock_config(**config_values):
        """
        Context manager to temporarily mock configuration values.
        
        This is specifically designed for PowerIt's config module.
        
        Example:
            with EnvironmentManager.mock_config(OFFLINE_MODE=True, GEMINI_API_KEY="test"):
                # Config values are mocked here
                pass
        """
        import sys
        
        # Save current config module if it exists
        original_config = sys.modules.get('config')
        
        # Create mock config
        class MockConfig:
            pass
        
        mock_config = MockConfig()
        
        # Set default values
        defaults = {
            'OFFLINE_MODE': False,
            'GEMINI_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key',
            'STORAGE_DIR': '/tmp/powerit_test_storage',
            'PRESENTATIONS_STORAGE_DIR': '/tmp/powerit_test_storage/presentations',
            'DATABASE_FILE': 'test_presentations.db',
        }
        
        # Apply defaults and overrides
        for key, value in {**defaults, **config_values}.items():
            setattr(mock_config, key, value)
        
        # Replace config module
        sys.modules['config'] = mock_config
        
        try:
            yield mock_config
        finally:
            # Restore original config
            if original_config is not None:
                sys.modules['config'] = original_config
            else:
                sys.modules.pop('config', None)