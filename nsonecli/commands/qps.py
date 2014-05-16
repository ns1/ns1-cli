#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

import base


class _qps(base.BaseCommand):

    """
    usage: nsone qps [-z <zone>] [-t <type>] [-d <domain>]

       -z <zone>    Limit statistics to the specified zone
       -t <type>    DNS record type (e.g., A, CNAME, MX ...)
       -d <domain>  Limit statistics to the specified FQDN

    """

    SHORT_HELP = "Retrieve real time queries per second"

    def run(self, args):
        # print "qps run: %s" % args
        stats = self.nsone.stats()
        print(stats.qps(zone=args['-z']))

qps = _qps()
