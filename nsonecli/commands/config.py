#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _config(BaseCommand):

    """
    usage: nsone config [show|set]

    Actions:
       show     Show the existing config
       set      Set a configuration variable

    Arguments:

    """

    SHORT_HELP = "View and manipulate configuration settings"

    def run(self, args):
        if args['show']:
            self.show()
        elif args['set']:
            self.set()
        else:
            self.show()

    def show(self):
        self.out(self.nsone.config)

config = _config()
