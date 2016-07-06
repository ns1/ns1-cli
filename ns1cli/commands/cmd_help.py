import six
from collections import defaultdict

import click

from ns1cli import __version__
from ns1cli.cli import cli as root_cli
from ns1cli.util import Formatter


class HelpFormatter(Formatter):

    def print_config(self, config):
        click.secho('Current Key: %s' % config.getCurrentKeyID(), bold=True)
        self.pretty_print(config.getKeyConfig())
        self.out(config)


@click.command('help',
               short_help='displays help for a sequence of commands')
@click.argument('subcommands', required=False, nargs=-1)
@click.pass_context
def cli(ctx, subcommands):
    """Displays usage/help for a given sequence of commands.

    \b
    Examples:
        ns1cli help record
        ns1cli help record answer
        ns1cli help record region
        ns1cli help record answer add
    """
    # import ipdb; ipdb.set_trace()
    cmd = root_cli
    for cmd_name in subcommands:
        cmd = cmd.get_command(ctx, cmd_name)

    if not cmd:
        raise click.BadParameter('Unknown command sequence')

    help_text = cmd.get_help(ctx)

    formatter = ctx.make_formatter()
    formatter.write_heading('NS1Cli v%s' % __version__)
    formatter.indent()
    with formatter.section('External Commands'):
        formatter.write_text('prefix external commands with "!"')
    with formatter.section('Internal Commands'):
        formatter.write_text('prefix internal commands with ":"')
        info_table = defaultdict(list)
        formatter.write(help_text)
        # for mnemonic, target_info in six.iteritems(root_cli.get_commands(ctx)):
        #     info_table[target_info[1]].append(mnemonic)
        # formatter.write_dl(
        #     (', '.join((':{0}'.format(mnemonic)
        #                 for mnemonic in sorted(mnemonics))), description)
        #     for description, mnemonics in six.iteritems(info_table)
        # )
    # return formatter.getvalue()
    help_text = formatter.getvalue()
    import ipdb; ipdb.set_trace()
    click.echo_via_pager(help_text)
