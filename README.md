# TokenTrackTUI ⬢ Neural Nexus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Support](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-early%20development-orange)](https://github.com/tokentracktui/tokentracktui)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**🚧 Early Development - Advanced TUI for LLM Token Usage Monitoring**

> **Note**: This project is in active early development (Sprint 1, Phase 1 completed). The interface and features are being built incrementally. See [Current Status](#-current-status) for what's implemented and [Roadmap](#-roadmap) for planned features.

TokenTrackTUI aims to be a sophisticated terminal interface that transforms complex LLM usage data into actionable insights through beautiful, modern visualization and intelligent design patterns inspired by neural networks and cloud computing paradigms.

## 🎯 Vision

A unified, beautiful TUI that provides:
- **Neural Network Interface**: Intelligent design inspired by neural networks and cloud computing
- **Multi-Cloud Support**: Single interface for multiple LLM providers (GCP, OpenAI, Anthropic, etc.)
- **Real-time Monitoring**: Live data streams with visual indicators
- **Advanced Analytics**: Cost tracking, trend analysis, and performance metrics

## 🚀 Current Status

### ✅ Phase 1 Complete (Sprint 1)
- **Core Architecture**: Textual-based application framework with async support
- **Configuration System**: TOML-based configuration with Pydantic validation
- **Neural Nexus Design**: Complete CSS theme system with responsive design
- **Developer Tools**: CLI interface, comprehensive testing, CI/CD pipeline
- **Project Foundation**: Poetry setup, linting, type checking, documentation

### 🔧 What Works Now
```bash
# Install dependencies
poetry install

# Run the basic app (shows initial interface)
poetry run python -c "from tokentracktui.core.app import create_app; create_app()"

# Run CLI commands
poetry run tokentracktui --version
poetry run tokentracktui --help

# Run tests
poetry run pytest
```

### 📱 Current Interface
The app currently shows:
- Neural Nexus styled header and footer
- Basic dashboard layout with placeholder content
- Loading screen with branding
- Responsive design that adapts to terminal size

## 🛠️ Development Setup

### Prerequisites
- **Python 3.9+** (tested on 3.9, 3.10, 3.11, 3.12)
- **Poetry** for dependency management
- **Modern Terminal** with Unicode support (iTerm2, Windows Terminal, GNOME Terminal)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/your-username/tokentracktui.git
cd tokentracktui

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run tests to verify setup
poetry run pytest

# Try the current interface
poetry run tokentracktui --help
```

### Development Commands
```bash
# Run tests with coverage
poetry run pytest --cov=tokentracktui

# Format code
poetry run black tokentracktui tests

# Lint code  
poetry run ruff check tokentracktui tests

# Type checking
poetry run mypy tokentracktui

# Run all quality checks
poetry run black . && poetry run ruff check . && poetry run mypy tokentracktui
```

## 📋 Roadmap

### 🎯 Phase 2 (Next - Sprint 1)
- **Mock Provider**: Basic data provider with realistic test data
- **Data Display**: Simple visualization of usage/cost data
- **Neural Graph**: Basic provider connection visualization
- **Financial Overview**: Cost summary widgets

### 🎯 Phase 3 (Sprint 1)
- **Provider SPI**: Complete Service Provider Interface
- **SQLite Integration**: Local data caching and storage
- **Basic Keyboard Actions**: Refresh, help, quit functionality

### 🎯 Future Sprints
- **Real Providers**: GCP, OpenAI, Anthropic integrations
- **Advanced Visualization**: Interactive charts and graphs
- **Export Capabilities**: JSON, CSV data export
- **Security Features**: Encrypted credential storage
- **Performance Optimization**: Caching, background refresh

## 🎨 Design System

The Neural Nexus design system features:
- **Neural Blue Gradients** (`#1e3a8a` → `#3b82f6`): Primary neural network theme
- **Cloud Silver Elements** (`#64748b` → `#f1f5f9`): Secondary cloud computing layers  
- **Data Flow Colors**: Green for active data, amber for warnings, red for errors
- **Responsive Layout**: Adapts to 80/120/160+ column terminals
- **Accessibility**: High contrast and monochrome modes included

## 🏗️ Architecture

### Current Structure
```
tokentracktui/
├── core/
│   ├── app.py          # Main Textual application (✅ implemented)
│   └── config.py       # Configuration management (✅ implemented)
├── utils/
│   └── logging.py      # Logging utilities (✅ implemented)
├── cli.py              # CLI interface (✅ implemented)
└── neural-nexus.tcss   # Design system CSS (✅ implemented)
```

### Technical Stack
- **UI Framework**: [Textual](https://textual.textualize.io/) for rich TUI
- **Configuration**: [Pydantic V2](https://docs.pydantic.dev/) + TOML
- **CLI**: [Typer](https://typer.tiangolo.com/) for command interface
- **Testing**: [pytest](https://pytest.org/) with async support
- **Code Quality**: Black, Ruff, MyPy

## 🤝 Contributing

**We welcome contributors!** This project is in early development and there are many opportunities to help shape its direction.

### 🎯 Good First Issues
- 📝 Improve documentation and examples
- 🧪 Add more test cases
- 🎨 Enhance the Neural Nexus design system
- 🔌 Work on provider integrations
- 🐛 Fix bugs and improve error handling

### 💡 How to Contribute
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with tests
4. **Run** quality checks (`poetry run pytest && poetry run black . && poetry run ruff check .`)
5. **Commit** with a clear message (see [Commit Guidelines](#commit-guidelines))
6. **Push** and create a **Pull Request**

### 📝 Commit Guidelines
We use conventional commits for clear history:
```bash
feat: add new provider interface
fix: resolve configuration loading bug  
docs: update installation instructions
test: add config validation tests
refactor: improve async error handling
```

### 🐛 Reporting Issues
- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template  
- **Questions**: Start a discussion in GitHub Discussions

## 📊 Project Status

### Test Coverage
- **Current**: 42% (27/27 tests passing)
- **Target**: 80%+ before v1.0

### Performance Metrics
- **App Creation**: ~50ms (target: <500ms) ✅
- **Test Suite**: 0.77s for 27 tests ✅
- **Memory Usage**: Minimal baseline ✅

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Textual](https://textual.textualize.io/)**: Amazing TUI framework that makes this possible
- **[Rich](https://rich.readthedocs.io/)**: Beautiful terminal formatting
- **The Python Community**: For excellent tooling and libraries

## 📞 Support & Community

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/tokentracktui/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/tokentracktui/discussions)
- 📖 **Wiki**: [Project Wiki](https://github.com/your-username/tokentracktui/wiki)

---

**🚧 This project is under active development. Star ⭐ the repo to follow progress!**

*Neural Nexus - Where AI monitoring meets beautiful design*
