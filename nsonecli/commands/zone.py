#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand, CommandException


class _zone(BaseCommand):

    """
    usage: nsone zone (list|info|create|update|delete) [ZONE]

    actions:
       list      List all active zones
       create    Create the specified zone
       info      Get zone details
       update    Update the details of the specified zone
       delete    Delete a zone and all records it contains

    If ZONE is specified, the action is limited to the target zone specified.

    """

    SHORT_HELP = "Create, retrieve, update, and delete zones"

    def run(self, args):
        # print("zone run: %s" % args)
        self._zoneAPI = self.nsone.zones()
        self._zone = args['ZONE']

        if args['list']:
            self.list()
        elif args['info']:
            self.info()

    def info(self):
        if not self._zone:
            raise CommandException(self, 'info requires a target zone')
        zdata = self._zoneAPI.retrieve(self._zone)
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

    def list(self):
        zlist = self._zoneAPI.list()
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
