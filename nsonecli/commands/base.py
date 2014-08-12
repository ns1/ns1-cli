#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

import json


class CommandException(Exception):

    def __init__(self, cmd, msg):
        self.cmd = cmd
        self.message = msg


class BaseCommand:

    SHORT_HELP = ""

    """:type : nsone.NSONE"""
    nsone = None

    def __init__(self):
        pass

    def jsonOut(self, d):
        print(json.dumps(d))

    def out(self, msg):
        print(msg)

    def isTextFormat(self):
        return self.nsone.config.get('cli', {}).get('output_format',
                                                    'text') == 'text'

    def _getBoolOption(self, val):
        val = str(val).lower().strip()
        if val == 'true' or val == 'yes':
            val = True
        if val == 'false' or val == 'no':
            val = False
        return bool(val)

    def checkWriteLock(self, args):
        if self.isWriteLocked(args['ZONE']) and not args['-f']:
            raise CommandException(self, 'Zone %s is write locked. '
                                         'Use -f to override.' % args['ZONE'])

    def isWriteLocked(self, zone=None):
        # XXX support doing something with zone
        return self.nsone.config.isKeyWriteLocked()

    def _longest(self, l):
        longest = 0
        for v in l:
            longest = max(longest, len(v))
        return longest

    def ppText(self, d, indent=0):
        import collections
        od = collections.OrderedDict(sorted(d.items()))
        longest = self._longest([k for (k, v) in od.items()])
        for (k, v) in od.items():
            if type(v) is str:
                self.out('%s%s: %s' % (' ' * indent, k.ljust(longest), v))
            elif type(v) is list or type(v) is tuple:
                str_v = [str(x) for x in v]
                self.out('%s%s: %s' % (' ' * indent, k.ljust(longest),
                                       ', '.join(str_v)))
            else:
                self.out('%s%s: %s' % (' ' * indent, k.ljust(longest), str(v)))
