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
    ctx.obj.zone_api = ctx.obj.rest.zones()


@cli.command('list', short_help='list all active zones')
@click.pass_context
def list(ctx):
    """Returns all active zones and basic zone configuration details
    for each.

    \b
    EXAMPLES:
        zone list
    """
    try:
        zlist = ctx.obj.zone_api.list()
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(zlist)
        return

    click.secho('ZONES:', bold=True)
    for z in zlist:
        ctx.obj.formatter.out('  ' + z['zone'])


@cli.command('info', short_help='get zone details')
@click.argument('zone')
@click.pass_context
def info(ctx, zone):
    """Returns a single active ZONE and its basic configuration details.
    For convenience, a list of records in the ZONE, and some basic details
    of each record, is also included.

    \b
    EXAMPLES:
        zone info test.com
    """
    try:
        zdata = ctx.obj.zone_api.retrieve(zone)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(zdata)
        return

    ctx.obj.formatter.print_zone(zdata)


@cli.command('create', short_help='create a new zone')
@click.argument('zone')
@write_options
@click.option('--link', help='Create linked zone pointing to given zone', type=str)
@click.option('--refresh', help='SOA Refresh', type=int)
@click.option('--retry', help='SOA Retry', type=int)
@click.option('--expiry', help='SOA Expiry', type=int)
@click.option('--nx_ttl', help='SOA NX TTL', type=int)
@click.pass_context
def create(ctx, nx_ttl, expiry, retry, refresh, link, zone):
    """Creates a new DNS ZONE. You must include at minimum the ZONE domain name.

    \b
    ZONE TYPES:
        1) standard zone (which has its own configuration and records)

        2) linked zone (which points to an existing standard zone, reusing its
           configuration and records)

    \b
    EXAMPLES:
        zone create test.com
        zone create --link test.com linked.com
        zone create --nx_ttl 300 with.option
        zone create --nx_ttl=300 with.option


    \b
    LINKED ZONES:
        For non-linked zones, you may specify optional zone configuration by including
        ttl (SOA record TTL), refresh, retry, expiry, and nx_ttl values, as in a SOA record.
        The zone is assigned DNS servers and appropriate NS records are automatically created,
        unless you create a secondary zone.

        To create a linked ZONE, you must include the --link option. It must be a string which
        references the TARGET zone (domain name) to link to. The TARGET zone must be owned by
        the same account that is creating the linked ZONE. If the link property is specified,
        no other zone configuration properties (such as refresh, retry, etc) may be specified,
        since they are all pulled from the TARGET zone. Linked zones, once created, cannot be
        configured at all and cannot have records added to them. They may only be deleted,
        which does not affect the TARGET zone at all.


    """
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

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(zdata)
        return

    ctx.obj.formatter.print_zone(zdata)


@cli.command('set', short_help='update zone attributes')
@click.argument('zone')
@write_options
@click.option('--refresh', help='SOA Refresh', type=int)
@click.option('--retry', help='SOA Retry', type=int)
@click.option('--expiry', help='SOA Expiry', type=int)
@click.option('--nx_ttl', help='SOA NX TTL', type=int)
@write_options
@click.pass_context
def set(ctx, nx_ttl, expiry, retry, refresh, zone):
    """Modify basic details of a DNS ZONE. Details include ttl (SOA record TTL),
    refresh, retry, expiry, or nx_ttl values, as in a SOA record.
    You may not change the ZONE name or other details.

    \b
    EXAMPLES:
        zone set --nt_ttl 200 --retry 5 test.com
        zone set -f --expiry 100 test.com
    """
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

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(zdata)
        return

    ctx.obj.formatter.print_zone(zdata)


@cli.command('delete',
             short_help='delete a zone and all records it contains')
@click.argument('zone')
@write_options
@click.pass_context
def delete(ctx, zone):
    """Destroys an existing DNS ZONE and all records in the ZONE.
    NS1 servers won't respond to queries for the zone or any of the records
    after you do this, and you cannot recover the deleted ZONE, so be careful!

    \b
    EXAMPLES:
        zone delete test.com
        zone delete -f test.com
    """
    ctx.obj.check_write_lock()

    try:
        ctx.obj.zone_api.delete(zone)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

