#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand, CommandException


class _qps(BaseCommand):

    """
    usage: nsone qps [ZONE] [[TYPE] [DOMAIN]]

    Arguments:
       ZONE    If specified, statistics are limited to this zone. If not
               specified, then statistics are account-wide.
       TYPE    DNS record type (e.g., A, CNAME, MX ...). Requires ZONE
               and <domain>
       DOMAIN  Limit statistics to the specified FQDN. Requires ZONE
               and <type>

    """

    SHORT_HELP = "Retrieve real time queries per second"

    def run(self, args):

        statsAPI = self.nsone.stats()

        zone = args['ZONE']
        type = args['TYPE']
        domain = args['DOMAIN']

        if type or domain:
            if not zone or not type or not domain:
                raise CommandException(self,
                                       'If you specify type or domain, '
                                       'you must specify all of zone, type, '
                                       'and domain.')
        qps = statsAPI.qps(zone=zone, domain=domain, type=type)
        if self.isTextFormat():
            self.out(qps['qps'])
        else:
            self.jsonOut(qps)


qps = _qps()
