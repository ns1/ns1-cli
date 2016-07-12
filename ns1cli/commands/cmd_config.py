import os

import click

from nsone.config import ConfigException
from ns1cli.cli import cli
from ns1cli.util import Formatter


class ConfigFormatter(Formatter):

    def print_config(self, config):
        try:
            click.secho('Current Key: %s' % config.getCurrentKeyID(), bold=True)
            self.pretty_print(config.getKeyConfig())
        except ConfigException as e:
            pass

        self.out(config)


@click.group('config',
             short_help='View and modify local configuration settings')
@click.pass_context
def cli(ctx):
    """View and manipulate configuration settings"""
    ctx.obj.formatter = ConfigFormatter(ctx.obj.get_config('output_format'))


@cli.command('show', short_help='Show the existing config')
@click.pass_context
def show(ctx):
    """Show the existing config

    \b
    EXAMPLES:
        ns1 config show
    """
    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(ctx.obj.rest.config._data)
        return

    ctx.obj.formatter.print_config(ctx.obj.rest.config)


@cli.command('set', short_help='Set the configuration key-value pair')
@click.argument('KEY')
@click.argument('VALUE')
@click.pass_context
def set(ctx, value, key):
    """Set the active configuration key-value

    \b
    EXAMPLES:
        ns1 config set write_lock true
        ns1 config set output_format json
    """
    ctx.obj.set_config(key, value)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(ctx.obj.rest.config._data)
        return

    ctx.obj.formatter.print_config(ctx.obj.rest.config)


@cli.command('key', short_help='Set the active configuration key id')
@click.argument('KEYID')
@click.pass_context
def key(ctx, keyid):
    """Set the active configuration key ID

    \b
    EXAMPLES:
        ns1 config key default
    """
    try:
        ctx.obj.rest.config.useKeyID(keyid)

        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(ctx.obj.rest.config._data)
            return

        click.secho('Using Key: %s' % keyid, bold=True)
        click.secho('Endpoint: %s' % ctx.obj.rest.config.getEndpoint(), bold=True)
    except ConfigException as e:
        raise click.ClickException(e.message)


@cli.command('save', short_help='Save the current config')
@click.argument('PATH', required=False)
@click.pass_context
def key(ctx, path):
    """Writes the current config to PATH if given,
    otherwise the ns1 directory.

    \b
    EXAMPLES:
        ns1 config save
        ns1 config save ~/ns1conf
    """
    if not path:
        path = os.path.join(ctx.obj.home_dir, ctx.obj.DEFAULT_CONFIG_FILE)

    try:
        ctx.obj.rest.config.write(path)

        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(ctx.obj.rest.config._data)
            return

        click.secho('Saved config at {}'.format(path), bold=True)
    except ConfigException as e:
        raise click.ClickException(e.message)


