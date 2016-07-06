import click
from ns1cli.cli import cli
from ns1cli.util import Formatter


class ConfigFormatter(Formatter):

    def print_config(self, config):
        click.secho('Current Key: %s' % config.getCurrentKeyID(), bold=True)
        self.pretty_print(config.getKeyConfig())
        self.out(config)


@click.group('config',
             short_help='view and modify local configuration settings')
@click.pass_context
def cli(ctx):
    """View and manipulate configuration settings"""
    ctx.obj.formatter = ConfigFormatter(ctx.obj.get_config('output_format'))


@cli.command('show', short_help='show the existing config')
@click.pass_context
def show(ctx):
    """Show the existing config

    Examples:

        config show
    """
    ctx.obj.formatter.print_config(ctx.obj.nsone.config)


@cli.command('set', short_help='set the configuration key-value')
@click.argument('KEY')
@click.argument('VALUE')
@click.pass_context
def set(ctx, value, key):
    """Set the active configuration key-value

    Examples:

        config set write_lock true

        config set output_format json
    """
    ctx.obj.set_config(key, value)
    ctx.obj.formatter.print_config(ctx.obj.nsone.config)


@cli.command('key', short_help='set the active configuration key ID')
@click.argument('KEYID')
@click.pass_context
def key(ctx, keyid):
    """Set the active configuration key ID

    Examples:

        config key default
    """
    ctx.obj.nsone.config.useKeyID(keyid)
    click.secho('Using Key: %s' % keyid, bold=True)
    click.secho('Endpoint: %s' % ctx.obj.nsone.config.getEndpoint(), bold=True)
