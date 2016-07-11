import atexit
import code
import os
import readline
import shlex
import sys

import click
from nsone.rest.resource import ResourceException

from ns1cli import __version__

APP_NAME = 'NS1 CLI'
BANNER = 'ns1 CLI version %s' % __version__


class NS1Repl(code.InteractiveConsole):

    HISTORY_FILE = 'ns1_history'
    HISTORY_LEN = 1000

    def __init__(self, ctx, cli):
        self.ctx = ctx
        self.cli = cli
        self.exit_cmds = ['quit', 'exit']

        code.InteractiveConsole.__init__(self)
        history_file = os.path.join(ctx.obj.home_dir, self.HISTORY_FILE)
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
        if not source:
            return

        command = shlex.split(source)

        if command[0] in self.exit_cmds:
            sys.exit(0)
        elif command[0] == 'clear':
            click.clear()
            return
        elif command[0] == 'help':
            click.echo(self.cli.get_help(self.ctx))
            return

        try:
            help_idx = command.index('help')
            command[help_idx] = '--help'
        except ValueError:
            pass

        subgroup = self.cli.get_command(self.ctx, command[0])

        if subgroup:
            try:
                with subgroup.make_context(None, command[1:], parent=self.ctx) as sub_ctx:
                    subgroup.invoke(sub_ctx)
                    sub_ctx.exit()
            except click.ClickException as e:
                e.show()
            except ResourceException as e:
                click.echo('REST API error: %s' % e.message)
                return
            except SystemExit:
                pass
        else:
            click.echo("unknown command '%s': try 'help'" % command[0])

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


