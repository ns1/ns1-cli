#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _zone(BaseCommand):

    """
    usage: nsone zone [-z <zone>] [action]

    options:
       -z <zone>    Limit statistics to the specified zone

    actions:
       create    Create the specified zone
       retrieve  If zone is specified, retrieve information on it. If no zone
                 is specified, get a list of all zones
       update    Update the details of the specified zone
       delete    Delete a zone and all records it contains
    """

    SHORT_HELP = "Create, update, and delete zones"

    def run(self, args):
        print("zone run: " % args)

zone = _zone()
