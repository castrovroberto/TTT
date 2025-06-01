"""
Main application class for TokenTrackTUI Neural Nexus.

Implements the core Textual application with screen management,
configuration loading, and the foundational Neural Nexus interface.
"""

import asyncio
import time
from pathlib import Path
from typing import Optional, Dict, Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, LoadingIndicator
from textual.containers import Container, Horizontal, Vertical
from textual import events

from tokentracktui.core.config import ConfigManager, Config, ConfigError
from tokentracktui.utils.logging import setup_logging, get_logger, log_performance
from tokentracktui import __version__, __codename__


logger = get_logger(__name__)


class NeuralHeader(Static):
    """Neural Nexus styled header widget."""
    
    DEFAULT_CSS = """
    NeuralHeader {
        height: 3;
        background: $neural-blue-dark;
        color: $text-primary;
        text-style: bold;
        padding: 1;
    }
    
    NeuralHeader .title {
        text-align: center;
        text-style: bold;
    }
    
    NeuralHeader .status {
        text-align: right;
        text-style: italic;
    }
    """
    
    def __init__(self, title: str = "TokenTrackTUI ⬢ Neural Nexus", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.status = "◐ Initializing"
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self.title, classes="title")
            yield Static(self.status, classes="status")
    
    def update_status(self, status: str) -> None:
        """Update the status indicator."""
        self.status = status
        self.refresh()


class NeuralFooter(Static):
    """Neural Nexus styled footer widget with quick actions."""
    
    DEFAULT_CSS = """
    NeuralFooter {
        height: 3;
        background: $surface-variant;
        color: $text-secondary;
        padding: 1;
    }
    
    NeuralFooter .actions {
        text-align: center;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.actions_text = "[R]efresh [H]elp [Q]uit"
    
    def compose(self) -> ComposeResult:
        yield Static(self.actions_text, classes="actions")
    
    def update_actions(self, actions: str) -> None:
        """Update the action text."""
        self.actions_text = actions
        self.refresh()


class LoadingScreen(Screen):
    """Loading screen shown during startup."""
    
    DEFAULT_CSS = """
    LoadingScreen {
        align: center middle;
    }
    
    LoadingScreen .loading-container {
        width: 60;
        height: 10;
        border: solid $primary;
        padding: 2;
    }
    
    LoadingScreen .loading-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    LoadingScreen .loading-subtitle {
        text-align: center;
        color: $text-secondary;
        margin-bottom: 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container(classes="loading-container"):
            yield Static(f"TokenTrackTUI v{__version__}", classes="loading-title")
            yield Static(__codename__, classes="loading-subtitle")
            yield LoadingIndicator()
            yield Static("Initializing Neural Nexus interface...", classes="loading-status")


class DashboardScreen(Screen):
    """Main dashboard screen with Neural Graph and overview."""
    
    BINDINGS = [
        Binding("r", "refresh", "Refresh", show=True),
        Binding("h", "help", "Help", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "config", "Config", show=False),
        Binding("g", "graph", "Graph", show=False),
    ]
    
    DEFAULT_CSS = """
    DashboardScreen {
        layout: vertical;
    }
    
    DashboardScreen .content-area {
        height: 1fr;
        layout: vertical;
        padding: 1;
    }
    
    DashboardScreen .main-panels {
        height: 1fr;
        layout: horizontal;
    }
    
    DashboardScreen .neural-graph-panel {
        width: 1fr;
        border: solid $primary;
        padding: 1;
        margin-right: 1;
    }
    
    DashboardScreen .overview-panel {
        width: 1fr;
        border: solid $surface-variant;
        padding: 1;
    }
    
    DashboardScreen .status-bar {
        height: 3;
        background: $surface;
        padding: 1;
    }
    """
    
    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.header = NeuralHeader()
        self.footer = NeuralFooter()
    
    def compose(self) -> ComposeResult:
        yield self.header
        
        with Container(classes="content-area"):
            with Container(classes="main-panels"):
                with Container(classes="neural-graph-panel"):
                    yield Static("◉ Provider Neural Graph", id="graph-title")
                    yield Static("Loading provider connections...", id="graph-content")
                
                with Container(classes="overview-panel"):
                    yield Static("⬢ Financial Overview", id="overview-title")
                    yield Static("Fetching usage data...", id="overview-content")
            
            with Container(classes="status-bar"):
                yield Static("Ready • No providers configured", id="status-message")
        
        yield self.footer
    
    async def on_mount(self) -> None:
        """Initialize dashboard when mounted."""
        logger.info("Dashboard screen mounted")
        self.header.update_status("◉ Live Mode")
        
        # Simulate loading data
        await self._load_dashboard_data()
    
    async def _load_dashboard_data(self) -> None:
        """Load and display dashboard data."""
        start_time = time.time()
        
        try:
            # Simulate data loading
            await asyncio.sleep(0.5)  # Simulate network delay
            
            # Update neural graph panel
            graph_content = self.query_one("#graph-content", Static)
            if self.config.providers:
                provider_lines = []
                for i, provider in enumerate(self.config.providers):
                    status = "◉" if provider.enabled else "○"
                    provider_lines.append(f"  {status} {provider.name} ({provider.type})")
                
                graph_content.update("\n".join(provider_lines))
            else:
                graph_content.update("No providers configured\nUse 'c' to configure providers")
            
            # Update overview panel
            overview_content = self.query_one("#overview-content", Static)
            overview_content.update(
                "Total Usage: --- tokens\n"
                "Total Cost: $---.--\n"
                "Active Providers: 0"
            )
            
            # Update status
            status_msg = self.query_one("#status-message", Static)
            provider_count = len([p for p in self.config.providers if p.enabled])
            status_msg.update(f"Ready • {provider_count} provider(s) configured")
            
            duration = time.time() - start_time
            log_performance("dashboard_load", duration, provider_count=provider_count)
            
        except Exception as e:
            logger.error(f"Failed to load dashboard data: {e}")
            self.notify("Failed to load dashboard data", severity="error")
    
    async def action_refresh(self) -> None:
        """Refresh dashboard data."""
        logger.info("Refreshing dashboard data")
        self.header.update_status("◐ Refreshing")
        
        try:
            await self._load_dashboard_data()
            self.header.update_status("◉ Live Mode")
            self.notify("Dashboard refreshed")
        except Exception as e:
            logger.error(f"Refresh failed: {e}")
            self.header.update_status("◉ Error")
            self.notify("Refresh failed", severity="error")
    
    async def action_help(self) -> None:
        """Show help screen."""
        self.notify("Help system not yet implemented")
    
    async def action_config(self) -> None:
        """Show configuration screen."""
        self.notify("Configuration screen not yet implemented")
    
    async def action_graph(self) -> None:
        """Show neural graph detail view."""
        self.notify("Graph detail view not yet implemented")
    
    async def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class TokenTrackTUIApp(App):
    """Main TokenTrackTUI Neural Nexus application."""
    
    TITLE = f"TokenTrackTUI {__version__} - {__codename__}"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("ctrl+d", "toggle_dark", "Toggle Dark Mode", show=False),
    ]
    
    def __init__(
        self,
        config_dir: Optional[Path] = None,
        log_level: str = "INFO",
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Set CSS path relative to the module
        import tokentracktui
        css_path = Path(tokentracktui.__file__).parent / "neural-nexus.tcss"
        self.css_path = [css_path] if css_path.exists() else []
        
        self.config_manager = ConfigManager(config_dir)
        self.config: Optional[Config] = None
        self.log_level = log_level
        self.startup_time = time.time()
        
        # Performance tracking
        self.performance_metrics: Dict[str, float] = {}
    
    async def on_mount(self) -> None:
        """Initialize the application."""
        mount_start = time.time()
        
        try:
            # Setup logging first
            self._setup_logging()
            logger.info(f"Starting TokenTrackTUI {__version__} - {__codename__}")
            
            # Show loading screen
            await self.push_screen(LoadingScreen())
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize main dashboard
            await self._initialize_dashboard()
            
            # Record startup performance
            startup_duration = time.time() - self.startup_time
            log_performance("app_startup", startup_duration)
            
            logger.info(f"Application startup completed in {startup_duration:.3f}s")
            
        except Exception as e:
            logger.error(f"Application startup failed: {e}")
            self.notify(f"Startup failed: {e}", severity="error")
            self.exit(1)
    
    def _setup_logging(self) -> None:
        """Setup application logging."""
        log_file = None
        
        # Use log file from config if available
        if hasattr(self, 'config') and self.config and self.config.app.log_file:
            log_file = Path(self.config.app.log_file)
        
        setup_logging(
            level=self.log_level,
            log_file=log_file,
            enable_textual_logging=True
        )
    
    async def _load_configuration(self) -> None:
        """Load application configuration."""
        try:
            self.config = self.config_manager.load_config()
            logger.info(f"Loaded configuration with {len(self.config.providers)} providers")
            
            # Update logging if config specifies different settings
            if self.config.app.log_level != self.log_level:
                self.log_level = self.config.app.log_level
                self._setup_logging()
            
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            # Create minimal config to continue
            self.config = Config()
            self.notify("Using default configuration", severity="warning")
    
    async def _initialize_dashboard(self) -> None:
        """Initialize and show the main dashboard."""
        # Small delay to show loading screen
        await asyncio.sleep(0.2)
        
        dashboard = DashboardScreen(self.config)
        await self.push_screen(dashboard)
        
        # Pop the loading screen
        self.pop_screen()
    
    async def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark
        mode = "dark" if self.dark else "light"
        logger.info(f"Switched to {mode} mode")
        self.notify(f"Switched to {mode} mode")
    
    async def action_quit(self) -> None:
        """Quit the application."""
        logger.info("Application shutdown requested")
        
        # Save any pending configuration changes
        try:
            if self.config:
                self.config_manager.save_config()
        except Exception as e:
            logger.warning(f"Failed to save config on exit: {e}")
        
        total_runtime = time.time() - self.startup_time
        log_performance("app_runtime", total_runtime)
        
        self.exit()
    
    def on_unmount(self) -> None:
        """Cleanup when application unmounts."""
        logger.info("Application unmounting")
    
    async def on_exception(self, exception: Exception) -> None:
        """Handle unhandled exceptions."""
        logger.error(f"Unhandled exception: {exception}", exc_info=True)
        self.notify(f"Internal error: {exception}", severity="error")


def create_app(
    config_dir: Optional[Path] = None,
    log_level: str = "INFO",
    **kwargs
) -> TokenTrackTUIApp:
    """Create and configure a TokenTrackTUI application instance."""
    return TokenTrackTUIApp(
        config_dir=config_dir,
        log_level=log_level,
        **kwargs
    ) 