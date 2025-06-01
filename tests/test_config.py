"""
Tests for configuration management functionality.
"""

import pytest
import tempfile
import toml
from pathlib import Path
from typing import Dict, Any

from tokentracktui.core.config import (
    Config,
    ConfigManager,
    ProviderConfig,
    UIConfig,
    AppConfig,
    ConfigError,
)


class TestProviderConfig:
    """Test ProviderConfig model."""
    
    def test_valid_provider_config(self):
        """Test creating a valid provider configuration."""
        config = ProviderConfig(
            name="Test Provider",
            type="mock",
            enabled=True,
            credentials={"api_key": "test"},
            settings={"test": True}
        )
        
        assert config.name == "Test Provider"
        assert config.type == "mock"
        assert config.enabled is True
        assert config.credentials == {"api_key": "test"}
        assert config.settings == {"test": True}
    
    def test_provider_defaults(self):
        """Test provider configuration defaults."""
        config = ProviderConfig(
            name="Test",
            type="mock"
        )
        
        assert config.enabled is True
        assert config.credentials == {}
        assert config.settings == {}
    
    def test_unknown_provider_type_warning(self, caplog):
        """Test warning for unknown provider types."""
        config = ProviderConfig(
            name="Test",
            type="unknown_provider"
        )
        
        assert config.type == "unknown_provider"
        # Warning should be logged but config should still be valid


class TestUIConfig:
    """Test UIConfig model."""
    
    def test_default_ui_config(self):
        """Test default UI configuration values."""
        config = UIConfig()
        
        assert config.theme == "neural-nexus"
        assert config.terminal_width_min == 80
        assert config.terminal_width_optimal == 120
        assert config.refresh_interval == 30
        assert config.animations_enabled is True
        assert config.unicode_enabled is True
        assert config.color_mode == "auto"


class TestAppConfig:
    """Test AppConfig model."""
    
    def test_default_app_config(self):
        """Test default application configuration values."""
        config = AppConfig()
        
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.cache_ttl == 3600
        assert config.data_retention_days == 90
        assert config.dry_run_mode is False


class TestConfig:
    """Test main Config model."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.version == "1.0.0"
        assert isinstance(config.app, AppConfig)
        assert isinstance(config.ui, UIConfig)
        assert config.providers == []
    
    def test_config_with_providers(self):
        """Test configuration with providers."""
        provider = ProviderConfig(name="Test", type="mock")
        config = Config(providers=[provider])
        
        assert len(config.providers) == 1
        assert config.providers[0].name == "Test"


class TestConfigManager:
    """Test ConfigManager functionality."""
    
    def test_init_with_custom_dir(self):
        """Test initialization with custom config directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = ConfigManager(config_dir)
            
            assert manager.config_dir == config_dir
            assert manager.config_file == config_dir / "tokentracktui_config.toml"
    
    def test_init_with_default_dir(self):
        """Test initialization with default config directory."""
        manager = ConfigManager()
        
        assert manager.config_dir.name == "tokentracktui"
        assert "tokentracktui_config.toml" in str(manager.config_file)
    
    def test_create_default_config(self):
        """Test creating default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            config = manager._create_default_config()
            
            assert isinstance(config, Config)
            assert len(config.providers) == 1
            assert config.providers[0].type == "mock"
            assert config.providers[0].name == "Mock Provider"
    
    def test_load_config_creates_default_if_missing(self):
        """Test loading config creates default when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            # Config file shouldn't exist initially
            assert not manager.config_file.exists()
            
            # Loading should create default config
            config = manager.load_config()
            
            assert isinstance(config, Config)
            assert manager.config_file.exists()
            assert len(config.providers) == 1
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            # Create and save a custom config
            provider = ProviderConfig(
                name="Custom Provider",
                type="gcp",
                settings={"project_id": "test-project"}
            )
            config = Config(providers=[provider])
            manager._config = config
            manager.save_config()
            
            # Load the config back
            loaded_config = manager.load_config()
            
            assert len(loaded_config.providers) == 1
            assert loaded_config.providers[0].name == "Custom Provider"
            assert loaded_config.providers[0].type == "gcp"
            assert loaded_config.providers[0].settings["project_id"] == "test-project"
    
    def test_load_invalid_toml_raises_config_error(self):
        """Test loading invalid TOML raises ConfigError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            # Write invalid TOML
            with open(manager.config_file, 'w') as f:
                f.write("invalid toml [ content")
            
            with pytest.raises(ConfigError, match="Invalid TOML syntax"):
                manager.load_config()
    
    def test_save_config_without_loaded_config_raises_error(self):
        """Test saving config without loading first raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            with pytest.raises(ConfigError, match="No configuration loaded"):
                manager.save_config()
    
    def test_get_config_loads_if_needed(self):
        """Test get_config loads configuration if not already loaded."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            assert manager._config is None
            
            config = manager.get_config()
            
            assert manager._config is not None
            assert isinstance(config, Config)
    
    def test_add_provider(self):
        """Test adding a provider configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            manager.load_config()  # Load default config
            
            initial_count = len(manager._config.providers)
            
            new_provider = ProviderConfig(name="New Provider", type="openai")
            manager.add_provider(new_provider)
            
            assert len(manager._config.providers) == initial_count + 1
            assert manager._config.providers[-1].name == "New Provider"
    
    def test_remove_provider(self):
        """Test removing a provider configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            # Create config with multiple providers
            providers = [
                ProviderConfig(name="Provider 1", type="mock"),
                ProviderConfig(name="Provider 2", type="gcp"),
            ]
            config = Config(providers=providers)
            manager._config = config
            
            # Remove one provider
            removed = manager.remove_provider("Provider 1")
            
            assert removed is True
            assert len(manager._config.providers) == 1
            assert manager._config.providers[0].name == "Provider 2"
            
            # Try to remove non-existent provider
            removed = manager.remove_provider("Non-existent")
            assert removed is False
    
    def test_get_enabled_providers(self):
        """Test getting enabled providers only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(Path(temp_dir))
            
            # Create config with enabled and disabled providers
            providers = [
                ProviderConfig(name="Enabled 1", type="mock", enabled=True),
                ProviderConfig(name="Disabled", type="gcp", enabled=False),
                ProviderConfig(name="Enabled 2", type="openai", enabled=True),
            ]
            config = Config(providers=providers)
            manager._config = config
            
            enabled = manager.get_enabled_providers()
            
            assert len(enabled) == 2
            assert all(p.enabled for p in enabled)
            assert {p.name for p in enabled} == {"Enabled 1", "Enabled 2"}


@pytest.fixture
def sample_config_data() -> Dict[str, Any]:
    """Sample configuration data for testing."""
    return {
        "version": "1.0.0",
        "app": {
            "log_level": "DEBUG",
            "cache_ttl": 7200,
        },
        "ui": {
            "theme": "custom-theme",
            "terminal_width_min": 100,
        },
        "providers": [
            {
                "name": "Test GCP",
                "type": "gcp",
                "enabled": True,
                "credentials": {},
                "settings": {"project_id": "test-project"}
            }
        ]
    }


def test_config_roundtrip_with_toml(sample_config_data):
    """Test configuration can be serialized to and from TOML."""
    # Create config from dict
    config = Config(**sample_config_data)
    
    # Convert to dict and back to TOML
    config_dict = config.model_dump()
    toml_string = toml.dumps(config_dict)
    
    # Parse TOML back to dict and create config
    parsed_dict = toml.loads(toml_string)
    parsed_config = Config(**parsed_dict)
    
    # Verify roundtrip integrity
    assert parsed_config.version == config.version
    assert parsed_config.app.log_level == config.app.log_level
    assert parsed_config.ui.theme == config.ui.theme
    assert len(parsed_config.providers) == len(config.providers)
    assert parsed_config.providers[0].name == config.providers[0].name 