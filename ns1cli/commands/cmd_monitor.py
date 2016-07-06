import click
from ns1cli.cli import cli
from ns1cli.util import Formatter
from nsone.rest.resource import ResourceException


class MonitorFormatter(Formatter):

    def print_monitor(self, mdata):
        regions = mdata['regions']
        status = mdata['status']
        rules = mdata['rules']
        del mdata['regions']
        del mdata['status']
        del mdata['rules']

        self.pretty_print(mdata)
        click.secho('REGIONS:', bold=True)
        for r in regions:
            self.out('    ' + r)
        click.secho('STATUS:', bold=True)
        for s in status:
            self.pretty_print(status[s], 4)
        click.secho('RULES:', bold=True)
        for r in rules:
            self.pretty_print(r, 4)


@click.group('monitor',
             short_help='view monitoring jobs')
@click.pass_context
def cli(ctx):
    """View monitoring jobs."""
    ctx.obj.formatter = MonitorFormatter(ctx.obj.get_config('output_format'))
    ctx.obj.monitor_api = ctx.obj.nsone.monitors()


@cli.command('list', short_help='list all active monitors')
@click.option('--include', multiple=True,
              help='Display additional data',
              type=click.Choice(['id', 'job_type']))
@click.pass_context
def list(ctx, include):
    """List all active monitors.

    \b
    Examples:
        monitor list
        monitor list --include id
        monitor list --include id --include job_type
    """
    try:
        mlist = ctx.obj.monitor_api.list()
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    click.secho('MONITORS:', bold=True)
    for m in mlist:
        ctx.obj.formatter.out('  name: ' + m['name'])
        if 'id' in include:
            ctx.obj.formatter.out('  id: ' + m['id'])
        if 'job_type' in include:
            ctx.obj.formatter.out('  job_type: ' + m['job_type'])
        ctx.obj.formatter.out('')


@cli.command('info', short_help='get monitor details')
@click.argument('JOBID')
@click.pass_context
def info(ctx, jobid):
    """Get monitor details

    \b
    Examples:
        monitor info 531a047f830f7803d5f0d2ca
    """
    try:
        mdata = ctx.obj.monitor_api.retrieve(jobid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    ctx.obj.formatter.print_monitor(mdata)
