# Contributing

This guide covers the development workflow, testing, and code quality standards.

## Prerequisites

**Required:** [uv](https://github.com/astral-sh/uv) - Python package manager

## Development Setup

### Install Dependencies

```bash
make deps
```

Installs everything you need:
- ✅ Runtime dependencies (Typer)
- ✅ Development dependencies (pytest, ruff, typer-cli, pre-commit)
- ✅ Pre-commit git hooks

**Pre-commit hooks** run automatically before each commit:
- Format code with Ruff
- Lint code with Ruff
- Run the test suite
- Generate documentation (fails if `USAGE.md` was edited manually)

### Validate Setup

```bash
make validate
```

Runs the complete quality check suite:
- ✅ Lint with Ruff (`make lint`)
- ✅ Format with Ruff (`make format`)
- ✅ Test with pytest (`make test`)

Use this to verify your setup or manually validate changes before committing. These are the same checks that pre-commit hooks run.

### Testing the CLI

**During development** - Test without installing:

```bash
uv run template-cli hello --name World
```

**Production testing** - Install and test:

```bash
# Install to ~/.local/bin
make install

# Run the installed CLI
template-cli hello --name World

# After code changes, reinstall with fresh cache
make upgrade
```

**PATH setup:** If the command isn't found, add `~/.local/bin` to your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Make Commands

Run `make` without arguments to see all available commands.

### Command Reference

| Command | Description |
|---------|-------------|
| `make deps` | Install dependencies and set up git hooks |
| `make validate` | Run lint, format, and test |
| `make install` | Install CLI globally to `~/.local/bin` |
| `make upgrade` | Reinstall CLI with fresh cache |
| `make docs` | Generate `USAGE.md` documentation |
| `make lint` | Check code with Ruff (no changes) |
| `make format` | Format code with Ruff |
| `make test` | Run test suite with pytest |
| `make github` | Configure branch protection (requires GitHub CLI) |

## Project Structure

```
.
├── template_package/                 # Python module package
│   ├── commands/                     # CLI command modules
│   ├── common/                       # Shared utilities
│   ├── models/                       # Data models
│   └── main.py                       # CLI entry point
├── tests/                            # Test suite
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # CI workflow
│   ├── SETUP.md                      # Workflow testing guide
│   └── setup-branch-protection.sh    # Branch protection setup script
├── .pre-commit-config.yaml           # Pre-commit hooks configuration
├── .python-version                   # Python version for uv
├── CONTRIBUTING.md                   # This file - for contributors
├── Makefile                          # Development commands
├── pyproject.toml                    # Project configuration
├── README.md                         # User documentation
├── USAGE.md                          # Generated CLI documentation
└── uv.lock                           # Locked dependencies
```

## Testing

### Unit Tests

Tests are located in `tests/test_*.py` and cover individual commands and services.

```bash
make test
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit to ensure:
- ✅ Code quality standards (lint and format)
- ✅ All tests pass
- ✅ Documentation is up to date

## Code Style

**Linting and formatting:** Ruff (configured in `pyproject.toml`)

The project follows standard Python conventions with automatic enforcement through pre-commit hooks and CI/CD.

## Need Help?

If you have questions or run into issues:
1. Check existing issues and pull requests
2. Open a new issue with details

Thank you for contributing! 🎉
