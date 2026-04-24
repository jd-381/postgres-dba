# Postgres DBA

A toolkit for Postgres DBAs.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) - Python package manager

## Installation

Install dba:

```bash
make install
```

Expected output:

```
dba installed successfully!
```

The CLI is installed to `~/.local/bin`. Make sure this directory is in your `$PATH`:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export PATH="$HOME/.local/bin:$PATH"
```

## Usage

See the [usage documentation](./USAGE.md) for all available commands and options.

### Quick Start

List available commands:

```bash
dba --help
```

Watch active queries:

```bash
dba proc -a -w 5
```

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup and guidelines.