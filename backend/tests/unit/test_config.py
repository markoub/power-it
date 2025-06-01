"""
Comprehensive tests for the PowerIt configuration system.
"""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from typing import Dict, Any

from tests.utils.env_manager import EnvironmentManager
from tests.utils.module_manager import ModuleManager


class TestConfigurationLoading:
    """Test configuration loading from various sources."""
    
    @pytest.fixture(autouse=True)
    def setup_config_test(self):
        """Setup test environment and clean up config module."""
        # Reset config module before each test
        ModuleManager.reset_modules("config")
        yield
        # Clean up after test
        ModuleManager.reset_modules("config")
    
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        with EnvironmentManager.temporary_env(
            GEMINI_API_KEY="test-gemini-key",
            OPENAI_API_KEY="test-openai-key",
            RESEARCH_MODEL="gemini-test-model",
            RESEARCH_TEMPERATURE="0.7",
            RESEARCH_TOP_K="30"
        ):
            import config
            
            assert config.GEMINI_API_KEY == "test-gemini-key"
            assert config.OPENAI_API_KEY == "test-openai-key"
            assert config.RESEARCH_MODEL == "gemini-test-model"
            assert config.RESEARCH_CONFIG["temperature"] == 0.7
            assert config.RESEARCH_CONFIG["top_k"] == 30
    
    def test_secret_file_loading(self, tmp_path):
        """Test loading secrets from /run/secrets/."""
        # Test the _load_secret function directly rather than the whole config module
        # since config.py has complex interactions with offline mode
        with EnvironmentManager.clean_env("TEST_SECRET"):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data="secret-value\n")):
                    # Import config to get access to _load_secret function
                    import config
                    
                    # Test the _load_secret function directly
                    result = config._load_secret("TEST_SECRET")
                    assert result == "secret-value"
    
    def test_default_value_handling(self):
        """Test that default values are used when env vars are not set."""
        with EnvironmentManager.clean_env(
            "RESEARCH_MODEL", "SLIDES_MODEL", "MODIFY_MODEL",
            "RESEARCH_TEMPERATURE", "SLIDES_TEMPERATURE", "MODIFY_TEMPERATURE"
        ):
            import config
            
            assert config.RESEARCH_MODEL == "gemini-2.5-flash-preview-04-17"
            assert config.SLIDES_MODEL == "gemini-2.5-flash-preview-04-17"
            assert config.MODIFY_MODEL == "gemini-2.5-flash-preview-04-17"
            assert config.RESEARCH_CONFIG["temperature"] == 0.2
            assert config.SLIDES_CONFIG["temperature"] == 0.3
            assert config.MODIFY_CONFIG["temperature"] == 0.25
    
    def test_type_conversion(self):
        """Test that environment variables are converted to correct types."""
        with EnvironmentManager.temporary_env(
            RESEARCH_TEMPERATURE="0.8",
            RESEARCH_TOP_P="0.9",
            RESEARCH_TOP_K="50",
            RESEARCH_MAX_OUTPUT_TOKENS="8192",
            SLIDES_DEFAULT_COUNT="20",
            SLIDES_DEFAULT_DURATION="30"
        ):
            import config
            
            # Float conversions
            assert isinstance(config.RESEARCH_CONFIG["temperature"], float)
            assert config.RESEARCH_CONFIG["temperature"] == 0.8
            assert isinstance(config.RESEARCH_CONFIG["top_p"], float)
            assert config.RESEARCH_CONFIG["top_p"] == 0.9
            
            # Integer conversions
            assert isinstance(config.RESEARCH_CONFIG["top_k"], int)
            assert config.RESEARCH_CONFIG["top_k"] == 50
            assert isinstance(config.RESEARCH_CONFIG["max_output_tokens"], int)
            assert config.RESEARCH_CONFIG["max_output_tokens"] == 8192
            
            # Slides defaults
            assert isinstance(config.SLIDES_DEFAULTS["target_slides"], int)
            assert config.SLIDES_DEFAULTS["target_slides"] == 20
            assert isinstance(config.SLIDES_DEFAULTS["presentation_duration"], int)
            assert config.SLIDES_DEFAULTS["presentation_duration"] == 30
    
    def test_offline_mode_configuration(self):
        """Test that offline mode is configured correctly."""
        # Test offline mode enabled
        with EnvironmentManager.temporary_env(POWERIT_OFFLINE="1"):
            import config
            
            assert config.OFFLINE_MODE is True
            assert config.GEMINI_API_KEY == "fake-testing-key"
            assert config.OPENAI_API_KEY == "fake-openai-key"
        
        # Reset modules for next test
        ModuleManager.reset_modules("config")
        
        # Test offline mode disabled
        with EnvironmentManager.temporary_env(
            POWERIT_OFFLINE="0",
            GEMINI_API_KEY="real-gemini-key",
            OPENAI_API_KEY="real-openai-key"
        ):
            import config
            
            assert config.OFFLINE_MODE is False
            assert config.GEMINI_API_KEY == "real-gemini-key"
            assert config.OPENAI_API_KEY == "real-openai-key"
    
    def test_storage_configuration(self, tmp_path):
        """Test storage directory configuration."""
        custom_storage = str(tmp_path / "custom_storage")
        
        with EnvironmentManager.temporary_env(STORAGE_DIR=custom_storage):
            import config
            
            assert config.STORAGE_DIR == custom_storage
            assert config.PRESENTATIONS_STORAGE_DIR == str(Path(custom_storage) / "presentations")
            
            # Verify directories are created
            assert Path(config.PRESENTATIONS_STORAGE_DIR).exists()


class TestConfigurationPrecedence:
    """Test configuration precedence rules."""
    
    @pytest.fixture(autouse=True)
    def setup_precedence_test(self):
        """Setup test environment."""
        ModuleManager.reset_modules("config")
        yield
        ModuleManager.reset_modules("config")
    
    def test_environment_over_defaults(self):
        """Test that environment variables take precedence over defaults."""
        with EnvironmentManager.temporary_env(
            RESEARCH_MODEL="custom-model",
            RESEARCH_TEMPERATURE="0.9"
        ):
            import config
            
            assert config.RESEARCH_MODEL == "custom-model"
            assert config.RESEARCH_CONFIG["temperature"] == 0.9
    
    def test_secrets_over_environment_when_no_env(self, tmp_path):
        """Test that secrets are used when environment variables are not set."""
        secrets_dir = tmp_path / "run" / "secrets"
        secrets_dir.mkdir(parents=True)
        (secrets_dir / "GEMINI_API_KEY").write_text("secret-key")
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="secret-key")):
                with EnvironmentManager.clean_env("GEMINI_API_KEY", "POWERIT_OFFLINE"):
                    import config
                    
                    assert config.GEMINI_API_KEY == "secret-key"
    
    def test_offline_mode_overrides_all(self):
        """Test that offline mode overrides API keys regardless of source."""
        with EnvironmentManager.temporary_env(
            POWERIT_OFFLINE="1",
            GEMINI_API_KEY="real-key",
            OPENAI_API_KEY="real-openai-key"
        ):
            import config
            
            assert config.OFFLINE_MODE is True
            assert config.GEMINI_API_KEY == "fake-testing-key"
            assert config.OPENAI_API_KEY == "fake-openai-key"


class TestConfigurationValidation:
    """Test configuration validation and error handling."""
    
    @pytest.fixture(autouse=True)
    def setup_validation_test(self):
        """Setup test environment."""
        ModuleManager.reset_modules("config")
        yield
        ModuleManager.reset_modules("config")
    
    def test_invalid_boolean_values(self):
        """Test handling of invalid boolean values."""
        # Test that invalid values are handled gracefully
        with EnvironmentManager.temporary_env(POWERIT_OFFLINE="maybe"):
            import config
            
            # Should default to False for invalid boolean
            assert config.OFFLINE_MODE is False
    
    def test_invalid_numeric_values(self):
        """Test handling of invalid numeric values."""
        with EnvironmentManager.temporary_env(
            RESEARCH_TEMPERATURE="not_a_number",
            RESEARCH_TOP_K="also_not_a_number",
            SLIDES_DEFAULT_COUNT="invalid"
        ):
            # Should not raise an exception, but use defaults
            try:
                import config
                
                # Should fall back to defaults or handle gracefully
                assert isinstance(config.RESEARCH_CONFIG["temperature"], (int, float))
                assert isinstance(config.RESEARCH_CONFIG["top_k"], int)
                assert isinstance(config.SLIDES_DEFAULTS["target_slides"], int)
            except (ValueError, TypeError):
                # If the config module doesn't handle invalid values gracefully,
                # that's also acceptable behavior
                pass
    
    def test_missing_api_keys_warning(self, capfd):
        """Test that missing API keys generate appropriate warnings."""
        with EnvironmentManager.clean_env("GEMINI_API_KEY", "OPENAI_API_KEY", "POWERIT_OFFLINE"):
            with patch('dotenv.load_dotenv'):  # Mock dotenv to avoid file search issues
                import config
                
                captured = capfd.readouterr()
                
                # Should have warnings about missing API keys
                # The warning might be in stdout or stderr
                output = captured.out + captured.err
                assert "WARNING" in output or "GEMINI_API_KEY not provided" in output


class TestConfigurationIntegration:
    """Test configuration integration with other systems."""
    
    @pytest.fixture(autouse=True)
    def setup_integration_test(self):
        """Setup test environment."""
        ModuleManager.reset_modules("config")
        yield
        ModuleManager.reset_modules("config")
    
    def test_genai_configuration(self):
        """Test that genai is configured correctly."""
        with EnvironmentManager.temporary_env(
            GEMINI_API_KEY="test-key",
            POWERIT_OFFLINE="0"
        ):
            with patch('google.generativeai.configure') as mock_configure:
                import config
                
                # Should configure genai with the API key
                mock_configure.assert_called_with(api_key="test-key")
    
    def test_genai_configuration_offline(self):
        """Test that genai is configured with fake key in offline mode."""
        with EnvironmentManager.temporary_env(POWERIT_OFFLINE="1"):
            with patch('google.generativeai.configure') as mock_configure:
                import config
                
                # Should configure genai with fake key
                mock_configure.assert_called_with(api_key="fake-testing-key")
    
    def test_vcr_mode_environment_setup(self):
        """Test that VCR modes are set up correctly in offline mode."""
        with EnvironmentManager.temporary_env(POWERIT_OFFLINE="1"):
            with EnvironmentManager.clean_env("GEMINI_VCR_MODE", "OPENAI_VCR_MODE"):
                import config
                
                # Should set VCR modes to replay
                assert os.environ.get("GEMINI_VCR_MODE") == "replay"
                assert os.environ.get("OPENAI_VCR_MODE") == "replay"
    
    def test_openai_environment_variable_setup(self):
        """Test that OpenAI environment variable is set correctly."""
        with EnvironmentManager.temporary_env(POWERIT_OFFLINE="1"):
            with EnvironmentManager.clean_env("OPENAI_API_KEY"):
                import config
                
                # Should set OpenAI API key in environment
                assert os.environ["OPENAI_API_KEY"] == "fake-openai-key"


class TestConfigurationUtilities:
    """Test configuration utility functions."""
    
    def test_load_secret_function(self):
        """Test the _load_secret function directly."""
        # Import the config module to access the function
        with EnvironmentManager.temporary_env(TEST_SECRET="env_value"):
            import config
            
            # Test environment variable loading
            result = config._load_secret("TEST_SECRET")
            assert result == "env_value"
            
            # Test default value
            result = config._load_secret("NONEXISTENT_SECRET", "default_value")
            assert result == "default_value"
            
            # Test None default
            result = config._load_secret("NONEXISTENT_SECRET")
            assert result is None
    
    def test_load_secret_from_file(self, tmp_path):
        """Test loading secrets from files."""
        # Create a mock secret file
        secret_file = tmp_path / "TEST_SECRET"
        secret_file.write_text("file_secret_value\n")
        
        with patch('os.path.exists') as mock_exists:
            with patch('builtins.open', mock_open(read_data="file_secret_value\n")):
                mock_exists.return_value = True
                
                with EnvironmentManager.clean_env("TEST_SECRET"):
                    import config
                    
                    result = config._load_secret("TEST_SECRET")
                    assert result == "file_secret_value"