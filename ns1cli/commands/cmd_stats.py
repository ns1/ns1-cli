import click
from ns1cli.cli import cli, State
from ns1cli.util import Formatter


class StatsFormatter(Formatter):

    def print_qps(self, zone_data, qdata):
        click.secho('%s %s %s' % (zone_data.get('zone', 'Account-Wide'),
                                  zone_data.get('domain', ''),
                                  zone_data.get('type', '')), bold=True)
        self.pretty_print(qdata)


def zone_argument(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.ZONE = value
        return value
    return click.argument('ZONE', expose_value=False, callback=callback)(f)


def domain_argument(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        # if no dot in the domain name, assume we should add zone
        if value.find('.') == -1:
            value = '%s.%s' % (value, state.ZONE)
        state.DOMAIN = value
        return value
    return click.argument('DOMAIN', expose_value=False, callback=callback)(f)


def type_argument(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.TYPE = value
        return value
    return click.argument('TYPE', expose_value=False, callback=callback)(f)


def record_arguments(f):
    # Order matters
    f = type_argument(f)
    f = domain_argument(f)
    f = zone_argument(f)
    return f


@click.group('stats', short_help='view usage/qps on zones and records')
@click.pass_context
def cli(ctx):
    """Get usage/qps on zones and records"""
    ctx.obj.formatter = StatsFormatter(ctx.obj.get_config('output_format'))
    ctx.obj.stats_api = ctx.obj.rest.stats()


@cli.command('qps', short_help='retrieve real time queries per second')
@click.argument('ZONE', required=False, metavar='[ZONE]')
@click.argument('DOMAIN', required=False, metavar='[[DOMAIN')
@click.argument('TYPE', required=False, metavar='TYPE]]')
@click.pass_context
def qps(ctx, type, domain, zone):
    """Retrieve real time queries per second for a zone or a record.

    \b
    ARGUMENTS:
       ZONE    If specified, statistics are limited to this zone. If not
               specified, then statistics are account-wide.
       TYPE    DNS record type (e.g., A, CNAME, MX ...). Requires ZONE
               and <domain>
       DOMAIN  Limit statistics to the specified FQDN. Requires ZONE
               and <type>

    \b
    EXAMPLES:
       ns1 qps test.com
       ns1 qps test.com test A
    """
    kwargs = {}
    if zone:
        kwargs['zone'] = zone

    if domain and type:
        if not zone:
            raise click.BadArgumentUsage(
                'A zone is required if given domain/type')

        if domain.find('.') == -1:
            domain = '%s.%s' % (domain, zone)

        kwargs['domain'] = domain
        kwargs['type'] = type

    qps = ctx.obj.stats_api.qps(**kwargs)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(qps)
        return

    ctx.obj.formatter.print_qps(kwargs, qps)


# @cli.command('usage', short_help='usage ..',
#              options_metavar='[options]')
# @click.argument('ZONE', required=False, metavar='[ZONE]')
# @click.argument('DOMAIN', required=False, metavar='[[DOMAIN]')
# @click.argument('TYPE', required=False, metavar='[TYPE]]')
# @click.pass_context
# def usage(ctx, type, domain, zone):
#   pass
