NS1 Command Line Interface (CLI)
==================================

> Please note:
> **At this time, the `NS1 CLI` package is [DEPRECATED](https://github.com/ns1/community/blob/master/project_status/DEPRECATED.md) and is
> not feature complete. We suggest using one of our other packages for
> production integrations.**

![Travis Build Status](https://travis-ci.org/ns1/ns1-cli.svg?branch=develop)

ns1cli is a both a command line program and REPL for accessing NS1, the Data Driven DNS platform.

## Command Line

```
$ ns1 -h
Usage: ns1 [OPTIONS] COMMAND [ARGS]...

  If no command is specified, the NS1 console is opened to accept
  interactive commands.

Options:
  -v                            Verbosity level
  --debug                       Enable debug mode
  --output [text|json]          Display format
  --ignore-ssl-errors           Ignore ssl certificate errors
  --key_id TEXT                 Use the specified api key id
  -k, --key TEXT                Use the specified api key
  -e, --endpoint TEXT           Use the specified server endpoint
  -c, --config_path PATH        Use the specified config file
  --transport [basic|requests]  Use the specified client transport
  -h, --help                    Show this message and exit.

Commands:
  config   View and modify local configuration settings
  data     View and modify data sources/feeds
  monitor  View monitoring jobs
  record   view and modify records in a zone
  stats    View usage/qps on zones and records
  zone     View and modify zone soa data
```

See `ns1 <command> --help` for more information on a specific command.

## REPL

` $ ns1 ` will start the REPL


Installation
============

__From PyPI__:

```bash
$ pip install ns1cli
```

__To enable autocomplete from the command-line__:

```bash
$ eval "$(_NS1_COMPLETE=source ns1)"
```

__Local Development__:

```bash
$ cd <ns1cli directory>
$ pip install --editable .
```

Configuration
=============

__ns1cli uses the [NS1 python client](https://github.com/ns1/nsone-python) to communicate with the [NS1 API](https://ns1.com/api/).__

 - ns1cli will by default attempt to load a configuration file from `$HOME/.ns1/config`
 - The configuration object used comes from the underlying NS1 python client
 - A history file for the REPL is saved at `$HOME/.ns1/ns1_history`


## TODO:

- REPL:
	- Autocomplete commands
	- `cmd <subcmd> help` is missing the command/subcommands in the help output.

- Search:
	- Autocomplete ZONE/DOMAIN/TYPE arguments.

- Zone:
   - Create secondary zones
   - Create zone from importing zonefile
   - Missing create zone attributes:
      - networks
      - secondary attrs(primary ip, primary_port)
   - Both `answer` and `region` `meta` subcommands are inconsistent:
      - `ns1 record answer meta-set` and `ns1 record answer meta-remove`
      - `ns1 record region meta-set` and `ns1 record region meta-remove`
      
      - The `meta` subcommands will be fixed when Click 7.0 is released:
      	- `ns1 record answer meta set` and `ns1 record answer meta remove`
      	- `ns1 record region meta set` and `ns1 record region meta remove`

      
- Record:
   - Update/Set record level attributes(TTL, RETRY, etc)
   
   - Answers
     - implement `ns1 record answer remove`
     
- Data:
	- Add `ns1 data feed publish` command

