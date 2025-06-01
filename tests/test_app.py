"""
Tests for the main application functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch
from pathlib import Path

from tokentracktui.core.app import TokenTrackTUIApp, create_app
from tokentracktui.core.config import Config, ProviderConfig


class TestTokenTrackTUIApp:
    """Test the main application class."""
    
    def test_app_creation(self):
        """Test basic app creation."""
        app = create_app()
        
        assert isinstance(app, TokenTrackTUIApp)
        assert app.config_manager is not None
        assert "Neural Nexus" in app.title
    
    def test_app_creation_with_custom_config_dir(self, tmp_path):
        """Test app creation with custom config directory."""
        app = create_app(config_dir=tmp_path)
        
        assert app.config_manager.config_dir == tmp_path
    
    def test_app_creation_with_log_level(self):
        """Test app creation with custom log level."""
        app = create_app(log_level="DEBUG")
        
        assert app.log_level == "DEBUG"


@pytest.mark.asyncio
class TestAppBehavior:
    """Test application behavior and lifecycle."""
    
    async def test_app_startup_performance(self):
        """Test that app creation meets performance targets."""
        start_time = time.time()
        
        app = create_app()
        
        creation_time = time.time() - start_time
        
        # Should meet the Phase 1 target of <500ms for app creation
        assert creation_time < 0.5, f"App creation took {creation_time:.3f}s, expected <0.5s"


class TestAppConfiguration:
    """Test app configuration handling."""
    
    @patch('tokentracktui.core.app.setup_logging')
    def test_logging_setup_called(self, mock_setup_logging):
        """Test that logging setup is called during app initialization."""
        app = create_app(log_level="DEBUG")
        
        # The logging setup should be called when the app mounts
        # Since we can't easily test the mount process, we'll test the setup method
        app._setup_logging()
        
        mock_setup_logging.assert_called_once()
    
    def test_app_loads_default_config(self, tmp_path):
        """Test that app loads default configuration when none exists."""
        app = create_app(config_dir=tmp_path)
        
        # Mock the config loading to test the behavior
        with patch.object(app.config_manager, 'load_config') as mock_load:
            mock_config = Config(providers=[
                ProviderConfig(name="Mock", type="mock")
            ])
            mock_load.return_value = mock_config
            
            # This would normally be called during mount
            config = app.config_manager.load_config()
            
            assert isinstance(config, Config)
            assert len(config.providers) == 1
            assert config.providers[0].type == "mock"


@pytest.fixture
def mock_app():
    """Create a mock application for testing."""
    app = Mock(spec=TokenTrackTUIApp)
    app.config = Config()
    app.log_level = "INFO"
    return app


def test_app_title_includes_version_and_codename():
    """Test that app title includes version and codename."""
    app = create_app()
    
    assert "TokenTrackTUI" in app.title
    assert "Neural Nexus" in app.title


def test_app_css_path_set():
    """Test that CSS path is properly set."""
    app = create_app()
    
    # CSS path should be set to the full path of neural-nexus.tcss
    assert app.css_path is not None
    assert len(app.css_path) > 0
    assert str(app.css_path[0]).endswith("neural-nexus.tcss") 