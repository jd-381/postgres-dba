# `dba`

A toolkit for Postgres DBAs.

**Usage**:

```console
$ dba [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show version
* `--help`: Show this message and exit.

**Commands**:

* `cron`: pg_cron administration
* `index`: Index administration
* `proc`: Processlist administration
* `repl`: Replication administration
* `table`: Table administration

## `dba cron`

pg_cron administration

**Usage**:

```console
$ dba cron [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `jobs`: Get cron jobs
* `logs`: Get cron job run details

### `dba cron jobs`

Get cron jobs

**Usage**:

```console
$ dba cron jobs [OPTIONS]
```

**Options**:

* `-j, --job INTEGER`: Job ID (optional)
* `-d, --database TEXT`: Name of database  [default: postgres]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

### `dba cron logs`

Get cron job run details

**Usage**:

```console
$ dba cron logs [OPTIONS]
```

**Options**:

* `-s, --status [all|failed|running|succeeded]`: Run status  [default: all]
* `-l, --limit INTEGER`: Limit rows  [default: 14]
* `-j, --job INTEGER`: Job ID (optional)
* `-d, --database TEXT`: Name of database  [default: postgres]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

## `dba index`

Index administration

**Usage**:

```console
$ dba index [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `progress`: Get index creation progress
* `size`: Get index sizes
* `unused`: Get unused indexes

### `dba index progress`

Get index creation progress

**Usage**:

```console
$ dba index progress [OPTIONS]
```

**Options**:

* `-d, --database TEXT`: Name of database  [required]
* `-w, --watch FLOAT`: Watch query interval (in seconds)  [default: 0]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

### `dba index size`

Get index sizes

**Usage**:

```console
$ dba index size [OPTIONS]
```

**Options**:

* `-d, --database TEXT`: Name of database  [required]
* `-t, --table TEXT`: Name of table as [schema.]table (defaults to &#x27;public&#x27; schema)
* `-i, --index TEXT`: Name of index
* `-l, --limit INTEGER`: Limit rows  [default: 10]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

### `dba index unused`

Get unused indexes

**Usage**:

```console
$ dba index unused [OPTIONS]
```

**Options**:

* `-d, --database TEXT`: Name of database  [required]
* `-t, --table TEXT`: Name of table as [schema.]table (defaults to &#x27;public&#x27; schema)
* `-l, --limit INTEGER`: Limit rows  [default: 10]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

## `dba proc`

Processlist administration

**Usage**:

```console
$ dba proc [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-a, --active`: Active queries only
* `--slots`: Show replication processes
* `--pids TEXT`: Show pids (ex: 1357,2468)
* `--ipids TEXT`: Ignore pids
* `--queries TEXT`: Show query IDs (ex: 1234567890,0987654321)
* `--iqueries TEXT`: Ignore query IDs
* `--users TEXT`: Show users (ex: ats_owner,postgres)
* `--iusers TEXT`: Ignore users
* `-l, --limit INTEGER`: Limit rows  [default: 10]
* `-w, --watch FLOAT`: Watch query interval (in seconds)  [default: 0]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

## `dba repl`

Replication administration

**Usage**:

```console
$ dba repl [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `heartbeat`: Get heartbeat info
* `pubs`: Get publication info
* `slots`: Get replication slot info
* `subs`: Get subscription info

### `dba repl heartbeat`

Get heartbeat info

**Usage**:

```console
$ dba repl heartbeat [OPTIONS]
```

**Options**:

* `-d, --database TEXT`: Name of database  [required]
* `-n, --name TEXT`: Tracking name (optional)
* `-w, --watch FLOAT`: Watch query interval (in seconds)  [default: 0]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

### `dba repl pubs`

Get publication info

**Usage**:

```console
$ dba repl pubs [OPTIONS]
```

**Options**:

* `-d, --database TEXT`: Name of database  [required]
* `-n, --name TEXT`: Publication name (optional)
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

### `dba repl slots`

Get replication slot info

**Usage**:

```console
$ dba repl slots [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: Slot name (optional)
* `-w, --watch FLOAT`: Watch query interval (in seconds)  [default: 0]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

### `dba repl subs`

Get subscription info

**Usage**:

```console
$ dba repl subs [OPTIONS]
```

**Options**:

* `-d, --database TEXT`: Name of database  [required]
* `-n, --name TEXT`: Subscription name (optional)
* `-w, --watch FLOAT`: Watch query interval (in seconds)  [default: 0]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.

## `dba table`

Table administration

**Usage**:

```console
$ dba table [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-d, --database TEXT`: Name of database  [required]
* `-t, --table TEXT`: Name of table as [schema.]table (defaults to &#x27;public&#x27; schema)  [required]
* `--debug`: Print SQL statements
* `--help`: Show this message and exit.
