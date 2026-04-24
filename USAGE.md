# `dba`

A CLI application demonstrating Typer best practices with commands and subcommands.

**Usage**:

```console
$ dba [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show version
* `--help`: Show this message and exit.

**Commands**:

* `hello`: Greet someone in various languages
* `mail`: Manage and interact with email messages

## `dba hello`

Greet someone in various languages

**Usage**:

```console
$ dba hello [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-n, --name TEXT`: Name to greet  [required]
* `-l, --language [english|spanish]`: Language for greeting  [default: english]
* `--debug`: Print debug messages
* `--help`: Show this message and exit.

## `dba mail`

Manage and interact with email messages

**Usage**:

```console
$ dba mail [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Delete mail
* `fetch`: Fetch mail
* `error`: Show example error

### `dba mail delete`

Delete mail

**Usage**:

```console
$ dba mail delete [OPTIONS]
```

**Options**:

* `-c, --count INTEGER`: Number of messages to delete  [required]
* `--debug`: Print debug messages
* `--help`: Show this message and exit.

### `dba mail fetch`

Fetch mail

**Usage**:

```console
$ dba mail fetch [OPTIONS]
```

**Options**:

* `--debug`: Print debug messages
* `--help`: Show this message and exit.

### `dba mail error`

Show example error

**Usage**:

```console
$ dba mail error [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
