#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _config(BaseCommand):

    """
    usage: nsone config <action>

    Actions:
       show     Show the existing config

    Arguments:

    """

    SHORT_HELP = "Show, load, save and set config options"

    def run(self, args):
        action = args['<action>']
        self.out(self.nsone.config)


config = _config()
