#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

"""
usage: nsone> <command> [<args>...]

Commands:
"""

import code
from docopt import docopt, DocoptExit
from nsonecli.commands.base import CommandException
from nsone.rest.service import ServiceException


class NSONERepl(code.InteractiveConsole):

    def __init__(self, cmdListDoc, cmdList):
        code.InteractiveConsole.__init__(self)
        self._doc = __doc__ + cmdListDoc
        self._cmdList = cmdList

    def runsource(self, source, filename="<input>", symbol="single"):
        """
        intercept nsone commands and run them
        """
        args = docopt(self._doc,
                      argv=source,
                      options_first=True)
        # print args
        cmd = args['<command>']
        cmdArgs = args['<args>']
        if type(cmdArgs) is not list:
            cmdArgs = [cmdArgs]
        subArgv = [cmd] + cmdArgs
        if cmd in self._cmdList.keys():
            svc = self._cmdList[cmd]
            try:
                subArgs = docopt(svc.__doc__, argv=subArgv)
            except DocoptExit as e:
                if cmd == 'help':
                    print(self._doc)
                else:
                    print(e.usage)
                return
            try:
                svc.run(subArgs)
            except ServiceException as e:
                print(e.message)
                return
            except CommandException as e:
                print(e.message)
                return
        else:
            # run as normal python
            # code.InteractiveConsole.runsource(self, source, filename, symbol)
            print("unknown command: try 'help'")

    def raw_input(self, prompt):
        return code.InteractiveConsole.raw_input(self, prompt='nsone> ')
