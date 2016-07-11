NS1 Command Line Interface (CLI)
==================================

![Travis Build Status](https://travis-ci.org/ns1/ns1-cli.svg?branch=develop)

ns1cli is a both a command line program and REPL for accessing NS1, the Data Driven DNS platform.

## Command Line

```
$ ns1 -h
Usage: ns1 help [OPTIONS] COMMAND [ARGS]...

  If no command is specified, the NS1 console is opened to accept
  interactive commands.

Options:
  -c, --config_path PATH        Use the specified config file
  -k, --key TEXT                Use the specified API Key
  -e, --endpoint TEXT           Use the specified server endpoint
  --transport [basic|requests]  Client transport
  --ignore-ssl-errors           Ignore SSL certificate errors
  -h, --help                    Show this message and exit.

Commands:
  config   view and modify local configuration settings
  data     view and modify data sources/feeds
  help     displays help for a sequence of commands
  monitor  view monitoring jobs
  record   view and modify records in a zone
  stats    view usage/qps on zones and records
  zone     view and modify zone SOA data
```

See `ns1 help <command>` for more information on a specific command.

## REPL

` $ ns1 ` will start the REPL


Installation
============

__From Pypi__:

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

ns1cli will by default attempt to load a configuration file from `$HOME/.nsone`.

 - The configuration object used comes from the underlying NS1 python client.


## TODO:

- REPL
	- Autocomplete commands

- Search
	- Autocomplete ZONE/DOMAIN/TYPE arguments.

- Zones
   - Create secondary zones
   - Create zone from importing zonefile
   - Missing create zone attributes:
      - networks
      - secondary attrs(primary ip, primary_port)
      
- Record
   - Update/Set record level attributes(TTL, RETRY, etc)
   
   - Answers
     - implement `ns1 record answer remove`
     


