import json

from click import echo, style, secho


class Formatter(object):
    def __init__(self, output_format):
        self.output_format = output_format

    def out(self, msg):
        echo(msg)

    def out_json(self, data):
        echo(json.dumps(data))

    def pretty_print(self, d, indent=0):
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

    def _longest(self, l):
        longest = 0
        for v in l:
            longest = max(longest, len(v))
        return longest


