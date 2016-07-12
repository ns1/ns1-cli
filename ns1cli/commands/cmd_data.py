import click
from ns1cli.cli import cli, write_options
from ns1cli.util import Formatter
from nsone.rest.resource import ResourceException


class DataFormatter(Formatter):

    def print_source(self, sdata):
        feeds = sdata.pop('feeds')
        self.pretty_print(sdata)
        if feeds:
            click.secho('FEEDS:', bold=True)
            for f in feeds:
                self.pretty_print(f, 4)

    def print_feed(self, fdata):
        dest = fdata.pop('destinations')
        self.pretty_print(fdata)
        if dest:
            click.secho('DESTINATIONS:', bold=True)
            for d in dest:
                self.pretty_print(d, 4)


@click.group('data',
             short_help='View and modify data sources/feeds')
@click.pass_context
def cli(ctx):
    """Create, retrieve, update, and delete data sources/feeds."""
    ctx.obj.formatter = DataFormatter(ctx.obj.get_config('output_format'))


@cli.group('source', short_help='View and modify data sources')
@click.pass_context
def source(ctx):
    """View and modify data sources."""
    ctx.obj.datasource_api = ctx.obj.rest.datasource()


@source.command('list', short_help='List all data sources')
@click.option('--include', multiple=True,
              help='Display additional data',
              type=click.Choice(['id', 'sourcetype']))
@click.pass_context
def list(ctx, include):
    """List of all connected data sources, and for each data source, all
    connected feeds including connected metadata table destinations.

    \b
    EXAMPLES:
        ns1 source list
        ns1 source list --include id
        ns1 source list --include id --include sourcetype
    """
    try:
        slist = ctx.obj.datasource_api.list()
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(slist)
        return

    click.secho('DATASOURCES:', bold=True)
    for s in slist:
        ctx.obj.formatter.out('  name: ' + s['name'])
        if 'id' in include:
            ctx.obj.formatter.out('  id: ' + s['id'])
        if 'sourcetype' in include:
            ctx.obj.formatter.out('  sourcetype: ' + s['sourcetype'])
        ctx.obj.formatter.out('')


@source.command('info', short_help='Get data source details')
@click.argument('SOURCEID')
@click.pass_context
def info(ctx, sourceid):
    """Display details for a single data source(given its SOURCEID), including
    configuration, all connected data feeds, and within data feeds, any connected
    metadata table (destinations).

    \b
    EXAMPLES:
        ns1 data source info 531a047f830f7803d5f0d2ca
    """
    try:
        sdata = ctx.obj.datasource_api.retrieve(sourceid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(sdata)
            return

        ctx.obj.formatter.print_source(sdata)


@source.command('create', short_help='Create a new data source')
@click.option('--config', type=(str, str), multiple=True,
              help='Set data source config value')
@write_options
@click.argument('SOURCETYPE', type=click.Choice(['nsone_v1', 'monitis', 'a10',
                                                 'nsone_monitoring', 'pingdom',
                                                 'cloudwatch', 'rackspace']))
@click.argument('NAME')
@click.pass_context
def create(ctx, name, sourcetype, config):
    """Creates a new data source with NAME and SOURCETYPE. You may create
    multiple data sources of the same type, e.g., to correspond to different
    accounts with a data provider.

    \b
    CONFIG:
        The --config option for the source must contain fields corresponding
        to the config description in /data/sourcetypes for the SOURCETYPE you
        specify. Some data sources are immediately connected; others enter a
        pending state awaiting activity from the data source, e.g., a verification
        request. See the documentation for the source from /data/sourcetypes.

    \b
    EXAMPLES:
        ns1 source create nsone_v1 new_nsone_source
        ns1 source create rackspace new_rackspace_source --config webhook_token token

    """
    ctx.obj.check_write_lock()

    options = {'config': {}}
    for key, val in config:
        options['config'][key] = val

    try:
        sdata = ctx.obj.datasource_api.create(name, sourcetype, **options)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(sdata)
            return

        ctx.obj.formatter.print_source(sdata)


@source.command('delete', short_help='Delete a data source')
@click.argument('SOURCEID')
@write_options
@click.pass_context
def delete(ctx, sourceid):
    """Removes an existing data source with SOURCEID and all connected feeds
    from the source. By extension, all metadata tables connected to those feeds
    will no longer receive updates. We will no longer accept updates on the
    Feed URL for this data source.

    \b
    EXAMPLES:
        ns1 source delete 1234
        ns1 source delete -f 1234
    """
    ctx.obj.check_write_lock()

    try:
        ctx.obj.datasource_api.delete(sourceid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        click.echo('{} deleted'.format(sourceid))


@cli.group('feed', short_help='View and modify data feeds')
@click.pass_context
def feed(ctx):
    """View and modify data feeds."""
    ctx.obj.datafeed_api = ctx.obj.rest.datafeed()


@feed.command('list', short_help='List all data feeds for a data source')
@click.option('--include', multiple=True,
              help='Display additional data',
              type=click.Choice(['id', 'destinations']))
@click.argument('SOURCEID')
@click.pass_context
def list(ctx, sourceid, include):
    """Lists all data feeds connected to a source with SOURCEID.
    Includes config details for each feed which match the
    feed_config specification from /data/sourcetypes, and optionally
    includes a list of metadata tables that are destinations
    for each feed.

    \b
    EXAMPLES:
        ns1 feed list SOURCEID
        ns1 feed list --include id SOURCEID
        ns1 feed list --include id --include destinations SOURCEID
    """
    try:
        flist = ctx.obj.datafeed_api.list(sourceid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(flist)
            return

        click.secho('DATAFEEDS:', bold=True)
        for f in flist:
            ctx.obj.formatter.out('  name: ' + f['name'])
            if 'id' in include:
                ctx.obj.formatter.out('  id: ' + f['id'])
            if 'destinations' in include:
                if not f['destinations']:
                    click.secho('  destinations: {}')
                else:
                    ctx.obj.formatter.out('  destinations:')
                    for d in f['destinations']:
                        ctx.obj.formatter.pretty_print(d, 4)
            ctx.obj.formatter.out('')


@feed.command('info', short_help='Get data feed details')
@click.argument('SOURCEID')
@click.argument('FEEDID')
@click.pass_context
def info(ctx, sourceid, feedid):
    """Display details of a single data feed with FEEDID, belonging to data source
    SOURCEID. Includes config details and any record, region, or answer metadata
    table destinations.

    \b
    EXAMPLES:
        ns1 data feed info 123.. 123..
    """
    try:
        fdata = ctx.obj.datafeed_api.retrieve(sourceid, feedid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(fdata)
            return

        ctx.obj.formatter.print_feed(fdata)


@feed.command('create', short_help='Create a new data feed')
@click.option('--config', type=(str, str), multiple=True,
              help='Set a data feed config value')
@write_options
@click.argument('SOURCEID')
@click.argument('NAME')
@click.pass_context
def create(ctx, sourceid, name, config):
    """Given an existing data source SOURCEID, connects a new data feed to
    the source with a given NAME and --config matching the specification
    in feed_config from /data/sourcetypes.

    \b
    EXAMPLES:
        ns1 source create 1234 new_data_feed
        ns1 source create 1234 new_data_feed --config label answer1

    """
    ctx.obj.check_write_lock()

    cfg = {key: val for key, val in config}

    try:
        fdata = ctx.obj.datafeed_api.create(sourceid, name, cfg)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)
    else:
        if ctx.obj.formatter.output_format == 'json':
            ctx.obj.formatter.out_json(fdata)
            return

        ctx.obj.formatter.print_feed(fdata)
