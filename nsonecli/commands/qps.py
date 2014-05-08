#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

import base


class _qps(base.BaseCommand):

    """usage: nsone qps [-z <zone>] [-t <type>] [-d <domain>]

    -h, --help

    zone    Limit statistics to the specified zone
    type    DNS record type (e.g., A, CNAME, MX ...)
    domain  Limit statistics to the specified FQDN

    """

    SHORT_HELP = "Retrieve real time queries per second"

    def __init__(self):
        pass

qps = _qps()
