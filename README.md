NS1 Command Line Interface (CLI)
==================================

![Travis Build Status](https://travis-ci.org/ns1/ns1-cli.svg?branch=develop)

ns1cli is a both a command line program and REPL for accessing NS1, the Data Driven DNS platform.

## Command Line

```
$ ns1 -h
usage: ns1 [-h] [-v ...] [-e <server>] [-k <key>] [-f <format>]
           [-t <transport>] [--ignore-ssl-errors] [--version]
           [<command>] [<args>...]

Options:
   -v                           Increase verbosity level. Can be used more
                                than once
   -k, --key <key>              Use the specified API Key
   -e, --endpoint <server>      Use the specified server endpoint
   -f, --format <format>        Output format: 'text'/'json'
                                [default: 'text']
   -t, --transport <transport>  Backend transport: 'basic'/'requests'/'twisted'
                                [default: 'requests'] if installed, O/W 'basic'
   --ignore-ssl-errors          Ignore SSL certificate errors
   -h, --help                   Show main usage help

If no command is specified, the NS1 console is opened to accept interactive
commands.

Commands:
   record    Create, retrieve, update, and delete records in a zone
   config    View and manipulate configuration settings
   help      Get help on a command
   zone      Create, retrieve, update, and delete zone SOA data
   qps       Retrieve real time queries per second

See 'ns1 help <command>' for more information on a specific command.

```

## REPL

[![asciicast](https://asciinema.org/a/5nazwezog280u44okccrrjhop.png)](https://asciinema.org/a/5nazwezog280u44okccrrjhop)

Installation
============

```bash
$ pip install ns1cli
```

Documentation
=============

http://ns1.com/api/



