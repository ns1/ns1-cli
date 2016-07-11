import click

from nsone.config import ConfigException
from ns1cli import __version__
from ns1cli.cli import cli as root_cli
from ns1cli.util import Formatter


class HelpFormatter(Formatter):

    def print_config(self, config):
        try:
            click.secho('Current Key: %s' % config.getCurrentKeyID(), bold=True)
            self.pretty_print(config.getKeyConfig())
        except ConfigException as e:
            pass

        self.out(config)


def solve(s):
    s = s.split('\n', 1)[-1]
    if s.find('\n') == -1:
        return s
    return s.rsplit('\n', 1)[0]


@click.command('help',
               short_help='displays help for a sequence of commands')
@click.argument('subcommands', required=False, nargs=-1)
@click.pass_context
def cli(ctx, subcommands):
    """Displays usage/help for a given sequence of commands.

    \b
    Examples:
        ns1 help record
        ns1 help record answer
        ns1 help record region
        ns1 help record answer add
    """
    cmd = root_cli
    for cmd_name in subcommands:
        cmd = cmd.get_command(ctx, cmd_name)

    if not cmd:
        raise click.BadParameter('Unknown command sequence')

    help_text = cmd.get_help(ctx)
    temp = solve(help_text)

    formatter = ctx.make_formatter()
    formatter.write_heading('NS1Cli v%s' % __version__)
    formatter.indent()
    formatter.write(help_text)
    help_text = formatter.getvalue()
    click.echo_via_pager(help_text)
