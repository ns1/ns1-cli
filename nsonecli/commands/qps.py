#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _qps(BaseCommand):

    """
    usage: nsone qps [-t <type>] [-d <domain>] [ZONE]

    Options:
       -t <type>    DNS record type (e.g., A, CNAME, MX ...). Requires ZONE
                    and <domain>
       -d <domain>  Limit statistics to the specified FQDN. Requires ZONE
                    and <type>

    If ZONE is specified, the statistics are limited to the specified zone. If
    none is specified, account-wide statistics are returned.

    """

    SHORT_HELP = "Retrieve real time queries per second"

    def run(self, args):
        print("qps run: %s" % args)
        statsAPI = self.nsone.stats()
        print(statsAPI.qps(zone=args['-z']))

qps = _qps()
