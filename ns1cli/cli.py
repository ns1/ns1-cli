import logging
import os
import sys

import click
from nsone import NSONE
from nsone.config import Config, ConfigException

from ns1cli.repl import NS1Repl, BANNER


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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


class State(object):

    APP_NAME = 'ns1'

    DEFAULT_CONFIG_FILE = 'config'

    DEFAULT_CONFIG = {'debug': False,
                      'output_format': 'text',
                      'verbosity': 0,
                      'write_lock': False,
                      'force': False}

    def __init__(self):
        self.home_dir = click.get_app_dir(self.APP_NAME, force_posix=True)
        if not os.path.exists(self.home_dir):
            os.makedirs(self.home_dir)

        # Config vars are saved/accessed through rest client.
        # self.rest.config['cli']
        self.rest = None
        self.cfg = self.DEFAULT_CONFIG
        self.rest_cfg_opts = {}

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.cfg['verbosity'] > 0:
            self.log(msg, *args)

    def get_config(self, key):
        """First checks the rest config cli attr, then the rest config itself.
        Raises ClickException if key doesnt exist."""
        if key in self.cfg:
            return self.cfg[key]
        else:
            try:
                return self.rest.config[key]
            except ConfigException:
                raise click.ClickException('Unknown config key {0}'.format(key))

    def set_config(self, key, value):
        """Sets config key-value pair."""
        if key in self.cfg:
            self.cfg[key] = value
            self.rest.config['cli'][key] = value
        else:
            self.rest.config[key] = value

    def check_write_lock(self):
        """Raises exception if ns1 rest client config `write_lock` is true."""
        if self.cfg['force']:
            return
        if self.cfg['write_lock']:
            raise click.BadOptionUsage('CLI is currently write locked.')

    def load_rest_client(self):
        """Loads ns1 rest client config"""
        opts = self.rest_cfg_opts

        # Create default config without any key
        cfg = Config()
        cfg.createFromAPIKey('')

        if opts.get('path', None):
            cfg.loadFromFile(opts['path'])
        elif opts.get('api_key'):
            cfg.createFromAPIKey(opts['api_key'])
        else:
            path = os.path.join(self.home_dir, self.DEFAULT_CONFIG_FILE)
            if os.path.exists(path):
                cfg.loadFromFile(path)

        if opts.get('api_key_id'):
            cfg.useKeyId(opts['api_key_id'])
        if opts.get('endpoint'):
            cfg['endpoint'] = opts['endpoint']
        if opts.get('transport'):
            cfg['transport'] = opts['transport']
        if opts.get('ignore_ssl'):
            cfg['ignore-ssl-errors'] = opts['ignore_ssl']

        if cfg['ignore-ssl-errors']:
            import requests
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        for k, v in self.cfg.items():
            cfg['cli'][k] = v

        self.rest = NSONE(config=cfg)


pass_state = click.make_pass_decorator(State, ensure=True)


def verbosity_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.cfg['verbosity'] = value
        return value
    return click.option('-v', count=True,
                        show_default=True,
                        expose_value=False,
                        help='Verbosity',
                        callback=callback)(f)


def debug_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.cfg['debug'] = value
        return value
    return click.option('--debug',
                        is_flag=True,
                        show_default=True,
                        expose_value=False,
                        help='Enables debug mode',
                        callback=callback)(f)


def output_format_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.cfg['output_format'] = value
        return value
    return click.option('-o', '--output',
                        show_default=True,
                        type=click.Choice(['text', 'json']),
                        expose_value=False,
                        help='Display format',
                        default='text',
                        callback=callback)(f)


def common_options(f):
    f = output_format_option(f)
    f = debug_option(f)
    f = verbosity_option(f)
    return f


def force_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.cfg['force'] = value
        return value
    return click.option('-f/--force',
                        expose_value=False,
                        is_flag=True,
                        help='Force: override the write lock if one exists',
                        callback=callback)(f)


def write_options(f):
    f = force_option(f)
    return f


def config_path_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.rest_cfg_opts['path'] = value
        # state.cfg = Config().loadFromFile(value)
        return value
    return click.option('-c', '--config_path',
                        expose_value=False,
                        help='Use the specified config file',
                        type=click.Path(exists=True),
                        callback=callback)(f)


def api_key_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.rest_cfg_opts['api_key'] = value
        return value
    return click.option('-k', '--key',
                        expose_value=False,
                        help='Use the specified API Key',
                        callback=callback)(f)


def api_key_id_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.rest_cfg_opts['api_key_id'] = value
        return value
    return click.option('--key_id',
                        expose_value=False,
                        help='Use the specified API Key ID',
                        callback=callback)(f)


def endpoint_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.rest_cfg_opts['endpoint'] = value
        return value
    return click.option('-e', '--endpoint',
                        expose_value=False,
                        help='Use the specified server endpoint',
                        callback=callback)(f)


def transport_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.rest_cfg_opts['transport'] = value
        return value
    return click.option('--transport',
                        expose_value=False,
                        help='Client transport',
                        default='requests',
                        type=click.Choice(['basic', 'requests']),
                        callback=callback)(f)


def ignore_ssl_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.rest_cfg_opts['ignore_ssl'] = value
        return value
    return click.option('--ignore-ssl-errors',
                        expose_value=False,
                        help='Ignore SSL certificate errors',
                        is_flag=True,
                        default=False,
                        callback=callback)(f)


def ns1_client_options(f):
    f = config_path_option(f)
    f = api_key_option(f)
    f = endpoint_option(f)
    f = api_key_id_option(f)
    f = transport_option(f)
    f = ignore_ssl_option(f)
    return f


@click.group(cls=NS1Cli, invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS)
@common_options
@ns1_client_options
@pass_state
@click.pass_context
def cli(ctx, state):
    """

    If no command is specified, the NS1 console is opened to accept interactive
    commands."""
    if state.rest_cfg_opts:
        try:
            state.load_rest_client()
        except ConfigException as e:
            raise click.ClickException(e.message)

    ctx.obj = state

    if not ctx.invoked_subcommand:
        repl = NS1Repl(ctx, cli)
        repl.interact(BANNER)
        sys.exit(0)
