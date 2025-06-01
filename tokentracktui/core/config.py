"""
Configuration management for TokenTrackTUI Neural Nexus.

Handles loading, validation, and management of user configuration including
provider settings, UI themes, and application preferences.
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from pydantic import BaseModel, Field, field_validator, ConfigDict
import logging

logger = logging.getLogger(__name__)


class ProviderConfig(BaseModel):
    """Configuration for a single provider."""
    
    name: str = Field(..., description="Display name for the provider")
    type: str = Field(..., description="Provider type (e.g., 'gcp', 'openai')")
    enabled: bool = Field(True, description="Whether this provider is enabled")
    credentials: Dict[str, Any] = Field(default_factory=dict, description="Provider credentials")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific settings")
    
    @field_validator('type')
    @classmethod
    def validate_provider_type(cls, v):
        allowed_types = ['mock', 'gcp', 'openai', 'anthropic', 'azure']
        if v not in allowed_types:
            logger.warning(f"Unknown provider type: {v}. Allowed: {allowed_types}")
        return v


class UIConfig(BaseModel):
    """UI and theming configuration."""
    
    theme: str = Field("neural-nexus", description="Active theme name")
    terminal_width_min: int = Field(80, description="Minimum terminal width")
    terminal_width_optimal: int = Field(120, description="Optimal terminal width")
    refresh_interval: int = Field(30, description="Auto-refresh interval in seconds")
    animations_enabled: bool = Field(True, description="Enable UI animations")
    unicode_enabled: bool = Field(True, description="Enable Unicode graphics")
    color_mode: str = Field("auto", description="Color mode: auto, dark, light, mono")


class AppConfig(BaseModel):
    """Application-level configuration."""
    
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    data_retention_days: int = Field(90, description="Data retention period")
    dry_run_mode: bool = Field(False, description="Enable dry-run mode")


class Config(BaseModel):
    """Main configuration object for TokenTrackTUI."""
    
    model_config = ConfigDict(extra="allow")  # Allow additional fields for extensibility
    
    version: str = Field("1.0.0", description="Config version")
    app: AppConfig = Field(default_factory=AppConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    providers: List[ProviderConfig] = Field(default_factory=list)


class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_dir: Optional[Union[Path, str]] = None):
        """Initialize config manager.
        
        Args:
            config_dir: Custom configuration directory. If None, uses default.
                       Can be a Path object, string, or None.
        """
        # Handle None or convert to Path
        if config_dir is None:
            self.config_dir = self._get_default_config_dir()
        else:
            # Handle Typer OptionInfo objects that might slip through
            if hasattr(config_dir, 'default') or str(type(config_dir).__name__) == 'OptionInfo':
                self.config_dir = self._get_default_config_dir()
            else:
                # Handle both Path objects and strings
                self.config_dir = Path(config_dir) if not isinstance(config_dir, Path) else config_dir
        
        self.config_file = self.config_dir / "tokentracktui_config.toml"
        self._config: Optional[Config] = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        if os.name == 'nt':  # Windows
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        else:  # Unix-like
            base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
        
        return base / 'tokentracktui'
    
    def load_config(self) -> Config:
        """Load configuration from file or create default."""
        if not self.config_file.exists():
            logger.info(f"Config file not found at {self.config_file}, creating default")
            self._config = self._create_default_config()
            self.save_config()
            return self._config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = toml.load(f)
            
            self._config = Config(**config_data)
            logger.info(f"Loaded configuration from {self.config_file}")
            return self._config
            
        except toml.TomlDecodeError as e:
            logger.error(f"Invalid TOML in config file: {e}")
            raise ConfigError(f"Invalid TOML syntax in {self.config_file}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            logger.info("Creating default configuration")
            self._config = self._create_default_config()
            return self._config
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        if not self._config:
            raise ConfigError("No configuration loaded to save")
        
        try:
            config_dict = self._config.model_dump()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                toml.dump(config_dict, f)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise ConfigError(f"Failed to save configuration: {e}")
    
    def _create_default_config(self) -> Config:
        """Create a default configuration with mock provider."""
        mock_provider = ProviderConfig(
            name="Mock Provider",
            type="mock",
            enabled=True,
            credentials={},
            settings={
                "generate_realistic_data": True,
                "data_points": 100
            }
        )
        
        return Config(
            providers=[mock_provider]
        )
    
    def get_config(self) -> Config:
        """Get the current configuration, loading it if necessary."""
        if not self._config:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values."""
        if not self._config:
            self.load_config()
        
        # Create a new config with updated values
        config_dict = self._config.model_dump()
        config_dict.update(kwargs)
        self._config = Config(**config_dict)
    
    def add_provider(self, provider_config: ProviderConfig) -> None:
        """Add a new provider configuration."""
        if not self._config:
            self.load_config()
        
        self._config.providers.append(provider_config)
        logger.info(f"Added provider: {provider_config.name}")
    
    def remove_provider(self, provider_name: str) -> bool:
        """Remove a provider by name. Returns True if removed."""
        if not self._config:
            self.load_config()
        
        original_count = len(self._config.providers)
        self._config.providers = [
            p for p in self._config.providers 
            if p.name != provider_name
        ]
        
        removed = len(self._config.providers) < original_count
        if removed:
            logger.info(f"Removed provider: {provider_name}")
        
        return removed
    
    def get_enabled_providers(self) -> List[ProviderConfig]:
        """Get all enabled provider configurations."""
        if not self._config:
            self.load_config()
        
        return [p for p in self._config.providers if p.enabled]


class ConfigError(Exception):
    """Raised when configuration operations fail."""
    pass 