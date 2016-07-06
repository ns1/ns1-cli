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
             short_help='view and modify data sources/feeds')
@click.pass_context
def cli(ctx):
    """Create, retrieve, update, and delete data sources/feeds.

    \b
    NS1's intelligent platform goes beyond even "advanced" DNS and introduces
    a new paradigm: Data Driven DNS. NS1's Data Driven DNS takes in real time
    feeds of data about your infrastructure, like server upness, load,
    response times, application metrics, and so on, and feeds them to our traffic
    management algorithms to adjust DNS responses on the fly.  No other DNS provider
    on the planet is as tightly coupled to your application.
    """
    ctx.obj.formatter = DataFormatter(ctx.obj.get_config('output_format'))


@cli.group('source', short_help='view and modify data sources')
@click.pass_context
def source(ctx):
    """View and modify data sources.

    \b
    Data Sources are the workhorses behind NS1's powerful Data Driven DNS.
    NS1 supports many different kinds of Data Sources, from widely used
    monitoring services to our own native NS1 API. Think of a single Data Source
    like an account for the associated service, that you're connecting to NS1.

    For example, if you create an Amazon Cloudwatch Data Source, it corresponds
    to your AWS account; you could also create a second Cloudwatch Data Source
    if you have a different AWS account to connect to NS1.
    """
    ctx.obj.datasource_api = ctx.obj.nsone.datasource()


@source.command('list', short_help='list all data sources')
@click.option('--include', multiple=True,
              help='display additional data',
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

    click.secho('DATASOURCES:', bold=True)
    for s in slist:
        ctx.obj.formatter.out('  name: ' + s['name'])
        if 'id' in include:
            ctx.obj.formatter.out('  id: ' + s['id'])
        if 'sourcetype' in include:
            ctx.obj.formatter.out('  sourcetype: ' + s['sourcetype'])
        ctx.obj.formatter.out('')


@source.command('info', short_help='get data source details')
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

    ctx.obj.formatter.print_source(sdata)


@source.command('create', short_help='create a new data source')
@click.option('--config', type=(str, str), multiple=True,
              help='set data source config value')
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
    if not ctx.obj.force:
        ctx.obj.check_write_lock()

    options = {'config': {}}
    for key, val in config:
        options['config'][key] = val

    try:
        sdata = ctx.obj.datasource_api.create(name, sourcetype, **options)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    ctx.obj.formatter.print_source(sdata)


@source.command('delete', short_help='delete a data source')
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
    if not ctx.obj.force:
        ctx.obj.check_write_lock()

    try:
        ctx.obj.datasource_api.delete(sourceid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)


@cli.group('feed', short_help='view and modify data feeds')
@click.pass_context
def feed(ctx):
    """View and modify data feeds.

    \b
    Data Feeds come from Data Sources and can be thought of like "topics".
    For example, if you have connected a Cloudwatch Data Source, you might
    create several Data Feeds from that source corresponding to different
    Cloudwatch monitors.

    Data Feeds are generally identified by service-specific details like monitor
    or health check ids, unique labels, etc.  Each Data Feed generates metadata
    updates specific to its "topic". For example, a Data Feed from a Cloudwatch
    monitor may update "up" metadata depending on the status of the monitor.A
    Data Feed, once it is created, can be connected to one or more metadata tables
    in any of your DNS records.

    It is perfectly normal to connect a single Data Feed to many different metadata tables.
    In fact, this can be incredibly powerful. For example, if you have a shared web server
    hosting several sites, you may have an answer corresponding to that server in the DNS
    records for all the sites. Connecting a monitoring Data Feed to those answers
    (and configuring appropriate filters) means they will all failover instantly when the
    monitor trips.
    """
    ctx.obj.datafeed_api = ctx.obj.nsone.datafeed()


@feed.command('list', short_help='list all data feeds for a data source')
@click.option('--include', multiple=True,
              help='display additional data',
              type=click.Choice(['id', 'destinations']))
@click.argument('SOURCEID')
@click.pass_context
def list(ctx, sourceid, include):
    """Lists all data feeds connected to a source with SOURCEID.
    Includes config details for each feed which match the
    feed_config specification from /data/sourcetypes, and also
    includes a list of metadata tables that are destinations
    for each feed.

    \b
    EXAMPLES:
        ns1 feed list SOURCEID
        ns1 feed list --include id SOURCEID
        ns1 feed list --include id --include sourcetype SOURCEID
    """
    try:
        flist = ctx.obj.datafeed_api.list(sourceid)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    click.secho('DATAFEEDS:', bold=True)
    for f in flist:
        ctx.obj.formatter.out('  name: ' + f['name'])
        if 'id' in include:
            ctx.obj.formatter.out('  id: ' + f['id'])
        if 'destinations' in include:
            ctx.obj.formatter.out('  destinations:')
            for d in f['destinations']:
                ctx.obj.formatter.pretty_print(d, 4)
        ctx.obj.formatter.out('')


@feed.command('info', short_help='get data feed details')
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

    ctx.obj.formatter.print_feed(fdata)


@feed.command('create', short_help='create a new data feed')
@click.option('--config', type=(str, str), multiple=True,
              help='set a data feed config value')
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
    if not ctx.obj.force:
        ctx.obj.check_write_lock()

    cfg = {key: val for key, val in config}

    try:
        fdata = ctx.obj.datafeed_api.create(sourceid, name, cfg)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    ctx.obj.formatter.print_feed(fdata)

