import click
from ns1cli.cli import cli
from ns1cli.util import Formatter
from nsone.rest.resource import ResourceException


class MonitorFormatter(Formatter):

    def print_monitor(self, mdata):
        regions = mdata.pop('regions')
        status = mdata.pop('status')
        rules = mdata.pop('rules')

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
             short_help='View monitoring jobs')
@click.pass_context
def cli(ctx):
    """View monitoring jobs."""
    ctx.obj.formatter = MonitorFormatter(ctx.obj.get_config('output_format'))
    ctx.obj.monitor_api = ctx.obj.rest.monitors()


@cli.command('list', short_help='List all active monitors')
@click.option('--include', multiple=True,
              help='Display additional data',
              type=click.Choice(['id', 'job_type']))
@click.pass_context
def list(ctx, include):
    """List of all monitoring jobs for the account, including configuration and
    current status details. Job status is shown per region, including the "global"
    region indicating the overal status of the monitoring job computed based on
    the status policy from the regional statuses. Status values both globally and
    per region include up, down, and pending.

    \b
    EXAMPLES:
        monitor list
        monitor list --include id
        monitor list --include id --include job_type
    """
    try:
        mlist = ctx.obj.monitor_api.list()
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(mlist)
            return

        click.secho('MONITORS:', bold=True)
        for m in mlist:
            ctx.obj.formatter.out('  name: ' + m['name'])
            if 'id' in include:
                ctx.obj.formatter.out('  id: ' + m['id'])
            if 'job_type' in include:
                ctx.obj.formatter.out('  job_type: ' + m['job_type'])
            ctx.obj.formatter.out('')


@cli.command('info', short_help='Get monitor details')
@click.argument('JOBID')
@click.pass_context
def info(ctx, jobid):
    """Display details for a specific monitoring job based on its JOBID, including
    configuration and current status details. Job status is shown per region,
    including the "global" region indicating the overall status of the monitoring
    job computed based on the status policy from the regional statuses.
    Status values both globally and per region include up, down, and pending.

    \b
    EXAMPLES:
        monitor info 531a047f830f7803d5f0d2ca
    """
    try:
        mdata = ctx.obj.monitor_api.retrieve(jobid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(mdata)
            return

        ctx.obj.formatter.print_monitor(mdata)
