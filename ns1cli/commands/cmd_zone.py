import click
from ns1cli.cli import cli, write_options
from ns1cli.util import Formatter
from nsone.rest.resource import ResourceException


class ZoneFormatter(Formatter):

    def print_zone(self, zdata):
        records = zdata.pop('records')
        self.pretty_print(zdata)

        if len(records) == 0:
            click.secho('NO RECORDS', bold=True)
            return

        click.secho('RECORDS:', bold=True)
        longestRec = self._longest([r['domain'] for r in records])
        for r in records:
            self.out(' %s  %s  %s' % (r['domain'].ljust(longestRec),
                                      r['type'].ljust(5),
                                      ', '.join(r['short_answers'])))


@click.group('zone',
             short_help='view and modify zone SOA data')
@click.pass_context
def cli(ctx):
    """Create, retrieve, update, and delete zone SOA data"""
    ctx.obj.formatter = ZoneFormatter(ctx.obj.get_config('output_format'))
    ctx.obj.zone_api = ctx.obj.nsone.zones()


@cli.command('list', short_help='List all active zones')
@click.pass_context
def list(ctx):
    """List all active zones

    \b
    Examples:
        zone list
    """
    try:
        zlist = ctx.obj.zone_api.list()
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    click.secho('ZONES:', bold=True)
    for z in zlist:
        ctx.obj.formatter.out('  ' + z['zone'])


@cli.command('info', short_help='Get zone details',
             options_metavar='[options]')
@click.argument('zone')
@click.pass_context
def info(ctx, zone):
    """Get zone details

    \b
    Examples:
        zone info test.com
    """
    try:
        zdata = ctx.obj.zone_api.retrieve(zone)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    ctx.obj.formatter.print_zone(zdata)


@cli.command('create', short_help='Create a new zone',
             options_metavar='[options]')
@click.argument('zone')
@write_options
@click.option('--link', help='Create linked zone pointing to given zone', type=str)
@click.option('--refresh', help='SOA Refresh', type=int)
@click.option('--retry', help='SOA Retry', type=int)
@click.option('--expiry', help='SOA Expiry', type=int)
@click.option('--nx_ttl', help='SOA NX TTL', type=int)
@click.pass_context
def create(ctx, nx_ttl, expiry, retry, refresh, link, zone):
    """Create a new zone

    \b
    Examples:
        zone create test.com
        zone create --link test.com linked.com
        zone create --nx_ttl 300 with.option
        zone create --nx_ttl=300 with.option
    """
    if not ctx.obj.force:
        ctx.obj.check_write_lock()

    options = {}
    if nx_ttl:
        options['nx_ttl'] = nx_ttl
    if expiry:
        options['expiry'] = expiry
    if retry:
        options['retry'] = retry
    if refresh:
        options['refresh'] = refresh

    if link:
        if options:
            raise click.UsageError('Cannot create linked zone with options besides the link source')
        options['link'] = link

    try:
        zdata = ctx.obj.zone_api.create(zone, **options)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    ctx.obj.formatter.print_zone(zdata)


@cli.command('set', short_help='Delete a zone and all records it contains',
             options_metavar='[options]')
@click.argument('zone')
@write_options
@click.option('--refresh', help='SOA Refresh', type=int)
@click.option('--retry', help='SOA Retry', type=int)
@click.option('--expiry', help='SOA Expiry', type=int)
@click.option('--nx_ttl', help='SOA NX TTL', type=int)
@write_options
@click.pass_context
def set(ctx, nx_ttl, expiry, retry, refresh, zone):
    """Set zone attributes

    \b
    Examples:
        zone set --nt_ttl 200 --retry 5 test.com
        zone set -f --expiry 100 test.com
    """
    if not ctx.obj.force:
        ctx.obj.check_write_lock()

    options = {}
    if nx_ttl:
        options['nx_ttl'] = nx_ttl
    if expiry:
        options['expiry'] = expiry
    if retry:
        options['retry'] = retry
    if refresh:
        options['refresh'] = refresh

    if not options:
        raise click.UsageError('Updating zone requires at least one option')

    try:
        zdata = ctx.obj.zone_api.update(zone, **options)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    ctx.obj.formatter.print_zone(zdata)


@cli.command('delete',
             short_help='Delete a zone and all records it contains',
             options_metavar='[options]')
@click.argument('zone')
@write_options
@click.pass_context
def delete(ctx, zone):
    """Delete a zone and all records it contains

    \b
    Examples:
        zone delete test.com
        zone delete -f test.com
    """
    if not ctx.obj.force:
        ctx.obj.check_write_lock()

    try:
        ctx.obj.zone_api.delete(zone)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

