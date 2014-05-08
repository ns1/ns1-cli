#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

import base


class _zone(base.BaseCommand):

    """
    zone help
    """

    SHORT_HELP = "Create, update, and delete zones"

    def __init__(self):
        pass

zone = _zone()
