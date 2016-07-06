import logging
import os
import sys

import click
from nsone import NSONE
from nsone.config import Config, ConfigException

from ns1cli.repl import NS1Repl

APP_NAME = 'NS1 CLI'
VERSION = '0.1'
BANNER = 'ns1 CLI version %s' % VERSION

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class State(object):

    CLI_CONFIG_KEYS = ('output_format', 'write_lock')

    def __init__(self):
        self.verbosity = 0
        self.debug = False
        self.output_format = 'text'

    def get_config(self, key):
        if key in self.CLI_CONFIG_KEYS:
            return self.nsone.config['cli'][key]
        else:
            return self.nsone.config[key]

    def set_config(self, key, value):
        if key in self.CLI_CONFIG_KEYS:
            self.nsone.config['cli'][key] = value
        else:
            self.nsone.config[key] = value

    def check_write_lock(self):
        if self.nsone.config['cli'].get('write_lock', False):
            raise click.BadOptionUsage('CLI is currently write locked.')

    def load_nsone_client(self, **kwargs):
        cfg = Config()

        if kwargs['config_path']:
            # cfg_file = os.path.join(click.get_app_dir(APP_NAME), 'config.ini')
            cfg.loadFromFile(kwargs['config_path'])
        elif kwargs['key']:
            # this will save a .nsone with this key if one doesn't already exist
            cfg.createFromAPIKey(kwargs['key'], maybeWriteDefault=True)
        else:
            cfg.loadFromFile(Config.DEFAULT_CONFIG_FILE)

        cfg['endpoint'] = kwargs['endpoint']
        cfg['transport'] = kwargs['transport']
        cfg['ignore-ssl-errors'] = kwargs['ignore_ssl']

        if cfg['ignore-ssl-errors']:
            if self.verbosity < 2:
                logging.captureWarnings(True)

        try:
            self.nsone = NSONE(config=cfg)
        except ConfigException as e:
            print(e.message)
            sys.exit(1)
        except IOError:
            print('No config file was found. Either specify an API key (with -k) '
                  'on the command line, or create %s' % Config.DEFAULT_CONFIG_FILE)
            sys.exit(1)

        self.set_config('output_format', self.output_format)

pass_state = click.make_pass_decorator(State, ensure=True)


def verbosity_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.verbosity = value
        return value
    return click.option('-v', '--verbose', count=True,
                        expose_value=False,
                        help='Enables verbosity',
                        callback=callback)(f)


def debug_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.debug = value
        return value
    return click.option('--debug/--no-debug',
                        expose_value=False,
                        help='Enables or disables debug mode.',
                        callback=callback)(f)


def output_format_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.output_format = value
        return value
    return click.option('-o', '--output_format',
                        type=click.Choice(['text', 'json']),
                        expose_value=False,
                        help='Output format',
                        default='text',
                        callback=callback)(f)


def common_options(f):
    f = output_format_option(f)
    f = verbosity_option(f)
    f = debug_option(f)
    return f


def force_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.force = value
        return value
    return click.option('-f/--force',
                        expose_value=False,
                        is_flag=True,
                        help='Force: override the write lock if one exists',
                        callback=callback)(f)


def write_options(f):
    f = force_option(f)
    return f


cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'commands'))


class NS1Cli(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('ns1cli.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


@click.group(cls=NS1Cli, invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--config_path', help='Use the specified config file',
              type=click.Path(exists=True))
@click.option('-k', '--key', help='Use the specified API Key')
@click.option('-e', '--endpoint', help='Use the specified server endpoint')
@click.option('--transport', help='Client transport', default='requests',
              type=click.Choice(['basic', 'requests']))
@click.option('--ignore-ssl-errors', help='Ignore SSL certificate errors',
              default=False, is_flag=True)
@pass_state
@click.pass_context
def cli(ctx, state, ignore_ssl_errors, transport, endpoint, key, config_path):
    """
    If no command is specified, the NS1 console is opened to accept interactive
    commands."""
    state.load_nsone_client(config_path=config_path,
                            key=key,
                            endpoint=endpoint,
                            transport=transport,
                            ignore_ssl=ignore_ssl_errors)

    ctx.obj = state

    if not ctx.invoked_subcommand:
        repl = NS1Repl(ctx, cli)
        repl.interact(BANNER)
        sys.exit(0)
