# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

"""
usage: ns1 [-h] [-v ...] [-e <server>] [-k <key>] [-f <format>]
           [-t <transport>] [--ignore-ssl-errors] [--version]
           [<command>] [<args>...]

Options:
   -v                           Increase verbosity level. Can be used more
                                than once
   -k, --key <key>              Use the specified API Key
   -e, --endpoint <server>      Use the specified server endpoint
   -f, --format <format>        Output format: 'text'/'json'
                                Default: 'text'
   -t, --transport <transport>  Backend transport: 'basic'/'requests'/'twisted'
                                Default: 'requests' if installed, O/W 'basic'
   --ignore-ssl-errors          Ignore SSL certificate errors
   -h, --help                   Show main usage help

If no command is specified, the NS1 console is opened to accept interactive
commands.

Commands:
"""

import sys
import logging
from docopt import docopt, DocoptExit
from nsone import NSONE
from nsone.config import Config, ConfigException
from nsone.rest.resource import ResourceException
from ns1cli.version import VERSION
from ns1cli.commands.base import BaseCommand, CommandException
from ns1cli.repl import NS1Repl
import ns1cli.commands


# gather commands
cmdList = {}
for sym, ins in ns1cli.commands.__dict__.items():
    if isinstance(ins, BaseCommand):
        cmdList[sym] = ins

# special case: give the full command list to help command so it can display
# usage for all commands
cmdList['help'].setCmdList(cmdList)

# add to doc help
cmdListDoc = ''
for cname, cmd in cmdList.items():
    cmdListDoc += '   %s%s\n' % (cname.ljust(10), cmd.SHORT_HELP)

__doc__ += cmdListDoc
__doc__ += "\nSee 'ns1 help <command>' for more information on a " \
           "specific command."


BANNER = 'ns1 CLI version %s' % VERSION


def main():
    args = docopt(__doc__,
                  version=BANNER,
                  options_first=True)
    # print('global arguments:')
    # print(args)
    # print('command arguments:')

    verbosity = args.get('-v', 0)
    if verbosity > 1:
        logging.basicConfig(level=logging.DEBUG)
    elif verbosity > 0:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.CRITICAL)
    # tweak requests logging
    if verbosity < 2:
        requests_log = logging.getLogger("requests")
        requests_log.setLevel(logging.WARNING)

    # if they specified an api key, use a custom config
    config = None
    if args['--key']:
        config = Config()
        # this will save a .nsone with this key if one doesn't already exist
        config.createFromAPIKey(args['--key'], maybeWriteDefault=True)
        config['verbosity'] = verbosity

    try:
        nsone = NSONE(config=config)
    except ConfigException as e:
        print(e.message)
        sys.exit(1)
    except IOError as e:
        print('No config file was found. Either specify an API key (with -k) '
              'on the command line, or create %s' % Config.DEFAULT_CONFIG_FILE)
        sys.exit(1)

    # do config overrides in nsone based on cmd args
    if args['--format']:
        nsone.config['cli']['output_format'] = args['--format']

    # do defaults
    if 'output_format' not in nsone.config.get('cli', {}):
        nsone.config['cli']['output_format'] = 'text'

    if args['--endpoint']:
        nsone.config['endpoint'] = args['--endpoint']

    if args['--ignore-ssl-errors']:
        nsone.config['ignore-ssl-errors'] = args['--ignore-ssl-errors']
        if verbosity < 2:
            logging.captureWarnings(True)

    if args['--transport']:
        nsone.config['transport'] = args['--transport']

    BaseCommand.nsone = nsone

    cmd = args['<command>']

    if not cmd:
        info = "\nType 'help' for help\n\nCurrent Key: %s\nEndpoint: %s" % \
               (nsone.config.getCurrentKeyID(), nsone.config.getEndpoint())
        repl = NS1Repl(cmdListDoc, cmdList)
        repl.interact(BANNER + info)
        sys.exit(0)

    cmdArgs = args['<args>']
    subArgv = [cmd] + cmdArgs
    # print "%s | %s | %s" % (cmd, cmdArgs, subArgv)
    if cmd in cmdList.keys():
        svc = cmdList[cmd]
        try:
            subArgs = docopt(svc.__doc__, argv=subArgv)
        except DocoptExit as e:
            if cmd == 'help':
                print(__doc__)
            else:
                print(e.usage)
            sys.exit(1)
        try:
            svc.run(subArgs)
        except ResourceException as e:
            print('REST API error: %s' % e.message)
        except CommandException as e:
            print(e.message)
            sys.exit(1)
    else:
        exit("%r is not a command. See 'ns1 help'." % cmd)
