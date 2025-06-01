"""
Command-line interface for TokenTrackTUI Neural Nexus.

Provides the main entry point and command-line argument parsing
using Typer for a modern CLI experience.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from tokentracktui import __version__, __codename__
from tokentracktui.core.app import create_app
from tokentracktui.utils.logging import setup_logging

# Initialize CLI app
cli = typer.Typer(
    name="tokentracktui",
    help="Neural Nexus - Advanced TUI for LLM Token Usage Monitoring",
    epilog="For more information, visit: https://github.com/tokentracktui/tokentracktui",
    no_args_is_help=False,
    rich_markup_mode="rich"
)

console = Console()


def version_callback(value: bool):
    """Show version information."""
    if value:
        version_text = Text()
        version_text.append("TokenTrackTUI ", style="bold blue")
        version_text.append(f"v{__version__}", style="bold green")
        version_text.append(f" - {__codename__}", style="italic cyan")
        
        console.print(Panel(
            version_text,
            title="Version Information",
            border_style="blue",
            padding=(1, 2)
        ))
        raise typer.Exit()


@cli.command()
def main(
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Custom configuration directory path",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        "-l",
        help="Set logging level",
        case_sensitive=False,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Run in dry-run mode (no actual API calls)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug mode with verbose logging",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version information and exit",
    ),
) -> None:
    """
    Launch TokenTrackTUI Neural Nexus - Advanced TUI for LLM Token Usage Monitoring.
    
    TokenTrackTUI provides a beautiful, terminal-native interface for monitoring
    LLM token usage and costs across multiple cloud providers with real-time
    insights and neural network-inspired visualizations.
    """
    
    # Adjust log level for debug mode
    if debug:
        log_level = "DEBUG"
        console.print("[yellow]Debug mode enabled[/yellow]")
    
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        console.print(f"[red]Error:[/red] Invalid log level '{log_level}'. "
                     f"Valid levels: {', '.join(valid_levels)}")
        raise typer.Exit(1)
    
    # Setup basic logging for CLI
    setup_logging(
        level=log_level.upper(),
        enable_console_logging=not debug,  # Avoid duplicate console logs in debug
        enable_textual_logging=False,
        enable_file_logging=True,
    )
    
    # Show startup banner
    if not debug:
        _show_startup_banner()
    
    try:
        # Create and run the application
        app = create_app(
            config_dir=config_dir,
            log_level=log_level.upper(),
        )
        
        # Handle dry-run mode
        if dry_run:
            console.print("[yellow]Dry-run mode enabled - no actual API calls will be made[/yellow]")
            # TODO: Set dry-run flag in app config
        
        # Run the TUI application
        app.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error:[/red] Application failed to start: {e}")
        if debug:
            console.print_exception()
        sys.exit(1)


@cli.command()
def config(
    show: bool = typer.Option(
        False,
        "--show",
        "-s",
        help="Show current configuration",
    ),
    edit: bool = typer.Option(
        False,
        "--edit",
        "-e",
        help="Open configuration in default editor",
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        "-r",
        help="Reset configuration to defaults",
    ),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Custom configuration directory path",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
) -> None:
    """
    Manage TokenTrackTUI configuration.
    
    View, edit, or reset application configuration including provider
    settings, UI preferences, and logging options.
    """
    from tokentracktui.core.config import ConfigManager
    
    config_manager = ConfigManager(config_dir)
    
    if reset:
        if typer.confirm("Are you sure you want to reset configuration to defaults?"):
            # TODO: Implement config reset
            console.print("[yellow]Configuration reset (not yet implemented)[/yellow]")
        return
    
    if edit:
        # TODO: Implement config editing
        console.print("[yellow]Configuration editing (not yet implemented)[/yellow]")
        return
    
    if show or not any([show, edit, reset]):
        # Show current configuration
        try:
            config = config_manager.load_config()
            console.print(Panel(
                f"Configuration file: {config_manager.config_file}\n"
                f"Version: {config.version}\n"
                f"Providers: {len(config.providers)}\n"
                f"Log level: {config.app.log_level}\n"
                f"Theme: {config.ui.theme}",
                title="Current Configuration",
                border_style="green"
            ))
        except Exception as e:
            console.print(f"[red]Error loading configuration:[/red] {e}")


@cli.command()
def providers(
    list_providers: bool = typer.Option(
        True,
        "--list",
        "-l",
        help="List configured providers",
    ),
    add: Optional[str] = typer.Option(
        None,
        "--add",
        "-a",
        help="Add a new provider (interactive)",
    ),
    remove: Optional[str] = typer.Option(
        None,
        "--remove",
        "-r",
        help="Remove a provider by name",
    ),
) -> None:
    """
    Manage LLM providers.
    
    List, add, or remove provider configurations for monitoring
    token usage across different LLM services.
    """
    # TODO: Implement provider management
    console.print("[yellow]Provider management (not yet implemented)[/yellow]")


def _show_startup_banner() -> None:
    """Display startup banner."""
    banner_text = Text()
    banner_text.append("⬢ ", style="bold cyan")
    banner_text.append("TokenTrackTUI", style="bold blue")
    banner_text.append(f" v{__version__}", style="green")
    banner_text.append("\n")
    banner_text.append(__codename__, style="italic cyan")
    banner_text.append("\n\nAdvanced TUI for LLM Token Usage Monitoring", style="dim")
    
    console.print(Panel(
        banner_text,
        title="Neural Nexus Interface",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()


if __name__ == "__main__":
    cli() 