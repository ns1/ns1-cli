#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _zone(BaseCommand):

    """
    Usage:
       ns1 zone list
       ns1 zone info ZONE
       ns1 zone create ZONE [-f] [options]
       ns1 zone delete [-f] ZONE
       ns1 zone set ZONE [-f] [options]

    Options:
       --refresh N  SOA Refresh
       --retry N    SOA Retry
       --expiry N   SOA Expiry
       --nx_ttl N   SOA NX TTL
       --link Z     Create linked zone pointing to zone Z
       -f           Force: override the write lock if one exists

    Zone Actions:
       list      List all active zones
       info      Get zone details
       create    Create a new zone
       delete    Delete a zone and all records it contains
       set       Set zone properties
    """

    SHORT_HELP = "Create, retrieve, update, and delete zone SOA data"

    def run(self, args):
        self._zone_api = self.nsone.zones()
        self._zone = args['ZONE']

        if args['list']:
            self.list()
        elif args['info']:
            self.info()
        elif args['delete']:
            self.delete(args)
        elif args['create']:
            self.create(args)
        elif args['set']:
            self.set(args)

    def _print_zone_model(self, zdata):
        if not self.isTextFormat():
            self.jsonOut(zdata)
            return

        records = zdata.pop('records')
        self.ppText(zdata)
        if len(records) == 0:
            self.out('NO RECORDS')
            return

        self.out('RECORDS:')
        longestRec = self._longest([r['domain'] for r in records])
        for r in records:
            self.out(' %s  %s  %s' % (r['domain'].ljust(longestRec),
                                      r['type'].ljust(5),
                                      ', '.join(r['short_answers'])))

    def create(self, args):
        self.checkWriteLock(args)
        options = self._get_options(args)
        zdata = self._zone_api.create(self._zone, **options)
        self._print_zone_model(zdata)

    def set(self, args):
        self.checkWriteLock(args)
        options = self._get_options(args)
        zdata = self._zone_api.update(self._zone, **options)
        self._print_zone_model(zdata)

    def delete(self, args):
        self.checkWriteLock(args)
        self._zone_api.delete(self._zone)

    def info(self):
        zdata = self._zone_api.retrieve(self._zone)
        self._print_zone_model(zdata)

    def list(self):
        zlist = self._zone_api.list()
        if self.isTextFormat():
            # weed out just the names
            for z in zlist:
                if not self._zone or (self._zone and z['zone'] == self._zone):
                    self.out(z['zone'])
        else:
            if self._zone:
                for z in zlist:
                    if self._zone and z['zone'] == self._zone:
                        self.jsonOut([z])
                        return
            else:
                self.jsonOut(zlist)

zone = _zone()
