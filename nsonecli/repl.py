#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

"""
usage: nsone> <command> [<args>...]

Commands:
"""

import readline
import code
from docopt import docopt, DocoptExit
from nsonecli.commands.base import CommandException
from nsone.rest.resource import ResourceException
import os
import sys
import atexit


class NSONERepl(code.InteractiveConsole):

    HISTORY_FILE = '~/.nsone_history'
    HISTORY_LEN = 1000

    def __init__(self, cmdListDoc, cmdList):
        code.InteractiveConsole.__init__(self)
        self._doc = __doc__ + cmdListDoc
        self._cmdList = cmdList
        history_file = os.path.expanduser(self.HISTORY_FILE)
        try:
            readline.read_history_file(history_file)
        except IOError:
            pass
        readline.parse_and_bind("tab: complete")
        readline.set_history_length(self.HISTORY_LEN)
        atexit.register(readline.write_history_file, history_file)

    def runsource(self, source, filename="<input>", symbol="single"):
        """
        intercept nsone commands and run them
        """
        args = docopt(self._doc,
                      argv=str(source).split(' '),
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
                    # in repl, replace the require preceding 'nsone' with ''
                    print(e.usage.replace(' nsone', ''))
                return
            try:
                svc.run(subArgs)
            except ResourceException as e:
                print('REST API error: %s' % e.message)
                return
            except CommandException as e:
                print(e.message)
                return
        else:
            # run as normal python
            # code.InteractiveConsole.runsource(self, source, filename, symbol)
            if cmd == 'quit' or cmd == 'exit':
                sys.exit(0)
            print("unknown command '%s': try 'help'" % cmd)

    def raw_input(self, prompt):
        return code.InteractiveConsole.raw_input(self, prompt='nsone> ')
