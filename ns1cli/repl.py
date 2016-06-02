#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

"""
usage: ns1> <command> [<args>...]

Commands:
"""

import readline
import code
from docopt import docopt, DocoptExit
from ns1cli.commands.base import CommandException
from nsone.rest.resource import ResourceException
import os
import sys
import atexit


class NS1Repl(code.InteractiveConsole):

    HISTORY_FILE = '~/.ns1_history'
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
        readline.set_history_length(self.HISTORY_LEN)
        readline.set_completer(self.complete)
        if 'libedit' in readline.__doc__:
            # sigh, apple
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")
        atexit.register(readline.write_history_file, history_file)

    def runsource(self, source, filename="<input>", symbol="single"):
        """
        intercept ns1 commands and run them
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
        # ls command == 'zone list'
        if cmd == 'ls':
            cmd = 'zone'
            subArgv = ['zone', 'list']
        #
        if cmd in self._cmdList.keys():
            svc = self._cmdList[cmd]
            try:
                subArgs = docopt(svc.__doc__, argv=subArgv)
            except DocoptExit as e:
                if cmd == 'help':
                    print(self._doc)
                else:
                    # in repl, replace the require preceding 'ns1' with ''
                    print(e.usage.replace(' ns1', ''))
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
            # run as normal python?
            # code.InteractiveConsole.runsource(self, source, filename, symbol)
            if cmd == 'quit' or cmd == 'exit':
                sys.exit(0)
            print("unknown command '%s': try 'help'" % cmd)

    def raw_input(self, prompt):
        return code.InteractiveConsole.raw_input(self, prompt='ns1> ')

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
            # origline = readline.get_line_buffer()
            # line = origline.lstrip()
            # stripped = len(origline) - len(line)
            # begidx = readline.get_begidx() - stripped
            # endidx = readline.get_endidx() - stripped

            # self.completion_matches = compfunc(text, line, begidx, endidx)
            self.completion_matches = []
        try:
            return self.completion_matches[state]
        except IndexError:
            return None
