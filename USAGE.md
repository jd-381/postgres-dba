# `template-cli`

A CLI application demonstrating Typer best practices with commands and subcommands.

**Usage**:

```console
$ template-cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show version
* `--help`: Show this message and exit.

**Commands**:

* `hello`: Greet someone in various languages
* `mail`: Manage and interact with email messages

## `template-cli hello`

Greet someone in various languages

**Usage**:

```console
$ template-cli hello [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-n, --name TEXT`: Name to greet  [required]
* `-l, --language [english|spanish]`: Language for greeting  [default: english]
* `--debug`: Print debug messages
* `--help`: Show this message and exit.

## `template-cli mail`

Manage and interact with email messages

**Usage**:

```console
$ template-cli mail [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Delete mail
* `fetch`: Fetch mail
* `error`: Show example error

### `template-cli mail delete`

Delete mail

**Usage**:

```console
$ template-cli mail delete [OPTIONS]
```

**Options**:

* `-c, --count INTEGER`: Number of messages to delete  [required]
* `--debug`: Print debug messages
* `--help`: Show this message and exit.

### `template-cli mail fetch`

Fetch mail

**Usage**:

```console
$ template-cli mail fetch [OPTIONS]
```

**Options**:

* `--debug`: Print debug messages
* `--help`: Show this message and exit.

### `template-cli mail error`

Show example error

**Usage**:

```console
$ template-cli mail error [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
