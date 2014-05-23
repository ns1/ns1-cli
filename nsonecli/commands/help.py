#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _help(BaseCommand):

    """
    usage: nsone help COMMAND

    Arguments:
       COMMAND  The command to get help on

    """

    SHORT_HELP = "Get help on a command"

    def __init__(self):
        self._cmdList = None

    def setCmdList(self, cmdList):
        self._cmdList = cmdList

    def run(self, args):
        cmd = args['COMMAND']
        if cmd not in self._cmdList:
            self.out('%s is an unknown command' % cmd)
        else:
            self.out(self._cmdList[cmd].__doc__)


help = _help()
