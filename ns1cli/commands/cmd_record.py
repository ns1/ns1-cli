import six

import click
from ns1cli.cli import State, write_options
from ns1cli.util import Formatter
from nsone.rest.resource import ResourceException


class RecordFormatter(Formatter):

    def print_record(self, rdata):
        ans = rdata.pop('answers')
        fil = rdata.pop('filters')
        reg = rdata.pop('regions')
        meta = rdata.pop('meta')

        self.pretty_print(rdata)

        click.secho('ANSWERS:', bold=True)
        for a in ans:
            self.pretty_print(a, 4)
        if len(fil):
            click.secho('FILTERS:', bold=True)
            for f in fil:
                self.pretty_print(f, 4)
        if reg:
            click.secho('REGIONS:', bold=True)
            for r, data in reg.items():
                click.secho('    ' + r)
                self.pretty_print(data, 4)
        if meta:
            click.secho('META:', bold=True)
            self.pretty_print(meta, 4)


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


def _has_meta(resource):
    return resource.get('meta', False)


@click.group('record',
             short_help='view and modify records in a zone')
@click.pass_context
def cli(ctx):
    """Create, retrieve, update, and delete records in a zone."""
    ctx.obj.formatter = RecordFormatter(ctx.obj.get_config('output_format'))
    ctx.obj.record_api = ctx.obj.rest.records()


@cli.command('info', short_help='get record details')
@record_arguments
@click.pass_context
def info(ctx):
    """Returns full configuration for a DNS record including basic config,
    answers, regions, filter chain configuration, and all metadata tables
    and data feeds attached to entities in the record.

    \b
    EXAMPLES:
        ns1 record info test.com test A
        ns1 record info test.com foo CNAME

    \b
    NOTES:
        ZONE, DOMAIN, and record TYPE must be fully specified:
            e.g. example.com www.example.com A returns the A record for
            www.example.com in the example.com zone.

        If no "dot" in DOMAIN, the zone is automatically appended to form a FQDN.
    """
    try:
        rdata = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                            ctx.obj.DOMAIN,
                                            ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


@cli.command('create',
             short_help='create a new record, optionally with simple answers')
@click.option('--target', type=str,
              help='create a linked record from an existing target')
@click.option('--ttl', type=int,
              help='ttl (defaults to default zone ttl)')
@click.option('--use-client-subnet', type=bool,
              help='set use of client-subnet EDNS option (defaults to true on new records)')
@write_options
@record_arguments
@click.option('--mx_priority', type=int, required=False, multiple=True,
              help='MX priority (ignored if type is not MX)')
@click.argument('ANSWERS', required=False, nargs=-1)
@click.pass_context
def create(ctx, answers, mx_priority, use_client_subnet, ttl, target):
    """Creates a new dns record in the specified ZONE, for the specified DOMAIN,
     of the given record TYPE.

    \b
    You may not create multiple records of the same TYPE for the same DOMAIN name in a ZONE.
    Instead, add new ANSWERs to the existing record. The default behavior if no filters are
    in the filter chain is to return all ANSWERs matching a query. The new record will take
    on the same networks as the ZONE it's in.

    \b
    RECORD TYPES:
        Currently supported record TYPEs are:
          - A, AAAA, ALIAS, AFSDB, CNAME, DNAME, HINFO, MX, NAPTR, NS, PTR, RP, SPF, SRV, TXT.

    \b
    ANSWERS:
        Multiple ANSWERs can be provided, along with RDATA fields for a DNS record of the specified TYPE.

    \b
    META DATA:
        Metadata tables (meta) may be specified in ANSWERs, in regions or in the record as a whole.
        The metadata tables may contain key/value pairs where valid keys and values are as described in the output of /metatypes.
        See:
          ns1 help record meta
          ns1 help record region meta
          ns1 help record answer meta

    \b
    DATA FEEDS:
        Anywhere metadata tables can go, data feeds can go as well.
        See:
          ns1 help data feed

    \b
    LINKED RECORDS:
        Instead of specifying answers and other details, you may create a "linked" record.
        This allows you reuse the configuration (including answers and metadata) from an
        existing record in NS1's systems. Linked records will respond in the exact same
        way as their targets at DNS resolution time, and can be used for maintaining
        complicated record configurations in a single record while pointing (linking)
        other lightweight records to it. Linked records must point to another record of
        the exact same record TYPE and do not have to exist in the same ZONE.

        To create a linked record, specify the --target as a string whose contents is
        the FQDN containing the config it should link to. If link is specified, no other
        record configuration (such as answers or meta) should be specified.

            record create --target source_domain_name test.com linked_domain_name A

    \b
    EXAMPLES:
        ns1 record create --ttl 200 test.com test A 1.1.1.1
        ns1 record create --target source test.com linked A
        ns1 record create test.com test A 1.1.1.1 2.2.2.2 3.3.3.3
        ns1 record create test.com mail MX --mx_priority 10 1.1.1.1

    \b
    NOTES:
        if record type is MX, each given answer MUST have priority:
          ... MX --mx_priority 10 1.1.1.1 --mx_priority 20 2.2.2.2

    """
    ctx.obj.check_write_lock()

    options = {}
    if ttl:
        options['ttl'] = ttl

    options['use_csubnet'] = use_client_subnet

    if target:
        if target.find('.') == -1:
            target = '%s.%s' % (target, ctx.obj.ZONE)
        options['link'] = target

    if ctx.obj.TYPE == 'MX':
        if len(set(mx_priority)) != len(mx_priority):
            raise click.BadOptionUsage('answers must have unique priorities')

        if len(mx_priority) != len(answers):
            raise click.BadArgumentUsage('every answer must have a priority')

        answers = six.itertools.izip(mx_priority, answers)
    elif mx_priority:
        raise click.BadOptionUsage('MX_priority is only allwed for MX records')

    options['answers'] = answers

    try:
        rdata = ctx.obj.record_api.create(ctx.obj.ZONE,
                                          ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, **options)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


@cli.command('delete', short_help='delete a record')
@write_options
@record_arguments
@click.pass_context
def delete(ctx):
    """Removes an existing record and all associated answers and configuration
    details. NS1 will no longer respond for this record once it is deleted, and
    it cannot be recovered, so use caution.

    \b
    Examples:
        ns1 record delete test.com test A
        ns1 record delete -f test.com test A

    \b
    NOTES:
        This operation deletes all answers associated with the domain and record type.
        If you want to delete individual answers, see:
            ns1 record answer remove
    """
    ctx.obj.check_write_lock()

    try:
        ctx.obj.record_api.delete(ctx.obj.ZONE, ctx.obj.DOMAIN, ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)


# META

@cli.group('meta', short_help='view and modify record meta')
@click.pass_context
def meta(ctx):
    """View and modify record meta data"""
    pass


@meta.command('set', short_help='set meta data key/value for a record')
@write_options
@record_arguments
@click.argument('METAKEY')
@click.argument('METAVAL')
@click.pass_context
def meta_set(ctx, metaval, metakey):
    """Set meta data key/value pairs for a record. This will set the meta data
    for the entire record, which will be used for an answer if there is no
    answer meta. See ns1 list meta types

    \b
    EXAMPLES:
         ns1 record meta set test.com geo A up false
    """
    ctx.obj.check_write_lock()

    # there is no rest api call to set meta without setting the entire
    # record, so we have to retrieve it, alter it, and send it back
    current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                          ctx.obj.DOMAIN,
                                          ctx.obj.TYPE)

    current['meta'][metakey] = metaval

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, meta=current['meta'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


@meta.command('remove', short_help='remove meta data key from a record')
@write_options
@record_arguments
@click.argument('METAKEY')
@click.pass_context
def meta_remove(ctx, metakey):
    """Remove meta data key/value pairs for a record. This will remove a meta
    data key for the entire record.

    \b
    EXAMPLES:
         ns1 record meta remove test.com geo A up
    """
    ctx.obj.check_write_lock()

    try:
        # there is no rest api call to set meta without setting the entire
        # answer, so we have to retrieve it, alter it, and send it back
        current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                              ctx.obj.DOMAIN,
                                              ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    try:
        del current['meta'][metakey]
    except KeyError:
        raise click.BadParameter(
            'record is missing metadata key %s' % metakey)

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, meta=current['meta'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


# ANSWERS

@cli.group('answer', chain=True, invoke_without_command=True,
           short_help='view and modify a records answers')
@click.pass_context
def answer(ctx):
    """View and modify record answer data
    """
    pass


@answer.command('add', short_help='add an answer to a record')
@write_options
@record_arguments
@click.option('--mx_priority', type=int, required=False, multiple=True,
              help='MX priority (ignored if type is not MX)')
@click.argument('ANSWER')
@click.pass_context
def add(ctx, mx_priority, answer):
    """Add an ANSWER to a record.

    \b
    EXAMPLES:
         ns1 record answer add geo.test geocname.geo.test CNAME 1.1.1.1
    """
    ctx.obj.check_write_lock()

    answer = [answer]

    if ctx.obj.TYPE == 'MX':
        if not mx_priority:
            raise click.BadArgumentUsage('MX answer must have a priority')
        answer.append(mx_priority)

    try:
        record = ctx.obj.rest.loadRecord(ctx.obj.DOMAIN,
                                          ctx.obj.TYPE,
                                          zone=ctx.obj.ZONE)
        record = record.addAnswers(answer)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(record.data)
        return

    ctx.obj.formatter.print_record(record.data)


# @answer.command('remove', short_help='remove an answer from a record')
# @write_options
# @record_arguments
# @click.argument('ANSWER')
# @click.pass_context
# def remove(ctx, answer):
#     """remove an answer from a record
#
#     Examples:
#
#          record answer remove geo.test geocname.geo.test CNAME 1.1.1.1
#     """
#     if not ctx.obj.force:
#         ctx.obj.check_write_lock()
#
#     answer = [answer]
#     record = ctx.obj.rest.loadRecord(ctx.obj.DOMAIN,
#                                       ctx.obj.TYPE,
#                                       zone=ctx.obj.ZONE)
#     #@TODO: NOT WORKING
#     record = record.removeAnswers(answer)
#     ctx.obj.formatter.print_record(record.data)


# @TODO: Have to wait for Click v7.0 for nested command chaining
# It is currently not possible for chain commands to be nested.
# This will be fixed in future versions of Click.
# @answer.group('meta', short_help='blah',
#               chain=True, invoke_without_command=True)
# @click.pass_context
# def answer_meta(ctx):
#     """
#
#     Examples:
#
#          record answer meta set geo.test geocname.geo.test CNAME add
#     """
#     pass


@answer.command('meta-set', short_help='set meta data key/value to an answer')
@write_options
@record_arguments
@click.argument('ANSWER')
@click.argument('METAKEY')
@click.argument('METAVAL')
@click.pass_context
def answer_meta_set(ctx, metaval, metakey, answer):
    """Set meta data KEY/VALUE pairs for an ANSWER. See ns1 list meta types

    \b
    EXAMPLES:
         ns1 record answer meta-set test.com geo A 1.2.3.4 georegion US-WEST
         ns1 record answer meta-set test.com geo A 6.7.8.9 georegion US-EAST
         ns1 record answer meta-set test.com geo A 3.3.3.3 georegion US-CENTRAL
    """
    ctx.obj.check_write_lock()

    try:
        # there is no rest api call to set meta without setting the entire
        # answer, so we have to retrieve it, alter it, and send it back
        current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                              ctx.obj.DOMAIN,
                                              ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    found = False
    for a in current['answers']:
        if a['answer'][0] == answer:
            if not _has_meta(a):
                a['meta'] = {}
            a['meta'][metakey] = metaval

            found = True
            break

    if not found:
        raise click.BadParameter(
            '%s is not a current answer for this record' % answer)

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, answers=current['answers'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


@answer.command('meta-remove', short_help='remove meta data key from an answer')
@write_options
@record_arguments
@click.argument('ANSWER')
@click.argument('METAKEY')
@click.pass_context
def answer_meta_remove(ctx, metakey, answer):
    """Remove a meta data KEY/VALUE pair from an ANSWER.

    \b
    EXAMPLES:
         ns1 record answer meta-remove test.com geo A 1.2.3.4 georegion
    """
    ctx.obj.check_write_lock()

    try:
        # there is no rest api call to set meta without setting the entire
        # answer, so we have to retrieve it, alter it, and send it back
        current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                              ctx.obj.DOMAIN,
                                              ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    for a in current['answers']:
        if a['answer'][0] == answer:
            if not _has_meta(a):
                raise click.BadParameter('%s has no meta' % answer)
            try:
                del a['meta'][metakey]
                # Remove the meta attr from answer if empty
                if not a['meta']:
                    del a['meta']
            except KeyError:
                raise click.BadParameter(
                    '%s missing metadata key %s' % (answer, metakey))

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, answers=current['answers'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


# REGIONS

# @TODO: Have to wait for Click v7.0 for nested command chaining
# It is currently not possible for chain commands to be nested.
# This will be fixed in future versions of Click.
# @region.group('meta', short_help='blah',
#               chain=True, invoke_without_command=True)
# @click.pass_context
# def region_meta(ctx):
#     """
#
#     Examples:
#
#          record region meta add geo.test geocname.geo.test CNAME us-west
#     """
#     pass

@cli.group('region', chain=True, invoke_without_command=True,
           short_help='view and modify a records answers')
@click.pass_context
def region(ctx):
    """View and modify record region data
    """
    pass


@region.command('add', short_help='add a region to a record')
@write_options
@record_arguments
@click.argument('REGION')
@click.pass_context
def add(ctx, region):
    """Add a REGION to a record.

    \b
    EXAMPLES:
         ns1 record region add geo.test geocname.geo.test CNAME us-west
    """
    ctx.obj.check_write_lock()

    try:
        # there is no rest api call to set meta without setting the entire
        # answer, so we have to retrieve it, alter it, and send it back
        current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                              ctx.obj.DOMAIN,
                                              ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    for reg in current['regions'].keys():
        if reg == region:
            raise click.BadParameter(
                '%s is already a current region for this record' % region)

    current['regions'][region] = {'meta': {}}

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, regions=current['regions'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


@region.command('remove', short_help='remove a region from a record')
@write_options
@record_arguments
@click.argument('REGION')
@click.pass_context
def remove(ctx, region):
    """Remove a REGION from a record.

    \b
    EXAMPLES:
         ns1 record region remove geo.test geocname.geo.test CNAME us-west
    """
    ctx.obj.check_write_lock()

    try:
        # there is no rest api call to set meta without setting the entire
        # answer, so we have to retrieve it, alter it, and send it back
        current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                              ctx.obj.DOMAIN,
                                              ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    found = False
    for reg in current['regions'].keys():
        if reg == region:
            found = True
            del current['regions'][region]

    if not found:
        raise click.BadParameter(
            '%s is not a current region for this record' % region)

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, regions=current['regions'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


@region.command('meta-set',
                short_help='set meta data key/value to a region')
@write_options
@record_arguments
@click.argument('REGION')
@click.argument('METAKEY')
@click.argument('METAVAL')
@click.pass_context
def region_meta_set(ctx, metaval, metakey, region):
    """Set a meta data KEY/VALUE for a REGION. See ns1 list meta types

    \b
    EXAMPLES:
         ns1 record region meta-set test.com geo A us-west up false
    """
    ctx.obj.check_write_lock()

    try:
        # there is no rest api call to set meta without setting the entire
        # answer, so we have to retrieve it, alter it, and send it back
        current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                              ctx.obj.DOMAIN,
                                              ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    found = False
    for reg in current['regions'].keys():
        if reg == region:
            found = True
            if not _has_meta(current['regions'][reg]['meta']):
                current['regions'][reg]['meta'] = {}
            current['regions'][reg]['meta'][metakey] = metaval

    if not found:
        raise click.BadParameter(
            '%s is not a current region for this record' % region)

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, regions=current['regions'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)


@region.command('meta-remove',
                short_help='remove meta data key from a region')
@write_options
@record_arguments
@click.argument('REGION')
@click.argument('METAKEY')
@click.pass_context
def region_meta_remove(ctx, metakey, region):
    """Remove a meta data KEY from a REGION.

    \b
    EXAMPLES:
         ns1 record region meta-remove test.com geo A us-west up
    """
    ctx.obj.check_write_lock()

    try:
        # there is no rest api call to set meta without setting the entire
        # answer, so we have to retrieve it, alter it, and send it back
        current = ctx.obj.record_api.retrieve(ctx.obj.ZONE,
                                              ctx.obj.DOMAIN,
                                              ctx.obj.TYPE)
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if not current['regions'].get(region, None):
        raise click.BadParameter(
            '%s is not a current region for this record' % region)
    if not _has_meta(current['regions'][region]):
        raise click.BadParameter(
            'region %s has no meta to remove' % region)
    try:
        del current['regions'][region]['meta'][metakey]
    except KeyError:
        raise click.BadParameter(
            'region %s has no metakey %s' % (region, metakey))

    try:
        rdata = ctx.obj.record_api.update(ctx.obj.ZONE, ctx.obj.DOMAIN,
                                          ctx.obj.TYPE, regions=current['regions'])
    except ResourceException as e:
        raise click.ClickException('REST API: %s' % e.message)

    if ctx.obj.formatter.output_format == 'json':
        ctx.obj.formatter.out_json(rdata)
        return

    ctx.obj.formatter.print_record(rdata)
