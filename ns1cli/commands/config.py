#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _config(BaseCommand):

    """
    usage: ns1 config [show]
           ns1 config key KEYID

    Actions:
       show     Show the existing config
       key      Set the active configuration key ID

    """

    SHORT_HELP = "View and manipulate configuration settings"

    def run(self, args):
        if args['show']:
            self.show()
        elif args['key']:
            self.key(args['KEYID'])
        else:
            self.show()

    def key(self, keyid):
        self.nsone.config.useKeyID(keyid)
        self.out('Using Key: %s' % keyid)
        self.out('Endpoint: %s' % self.nsone.config.getEndpoint())

    def show(self):
        self.out('Current Key: %s' % self.nsone.config.getCurrentKeyID())
        self.ppText(self.nsone.config.getKeyConfig())
        self.out(self.nsone.config)

config = _config()
