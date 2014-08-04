#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _record(BaseCommand):

    """
    usage: nsone record info ZONE DOMAIN TYPE
           nsone record create ZONE DOMAIN TYPE options (ANSWER ...)
           nsone record set ZONE DOMAIN TYPE options
           nsone record answers ZONE DOMAIN TYPE [options] (ANSWER ...)

    Record operations. You may leave the zone name off of DOMAIN (do not end it
    with a period)

    Options:
       --ttl N                          TTL (Defaults to default zone TTL)
       --use-client-subnet BOOL         Set use of client-subnet EDNS option
                                        (Defaults to True on new records)
       -f                               Force: override the write lock if one
                                        exists

    Record Actions:
       info      Get record details
       create    Create a new record
       set       Set record properties
       answers   Set one or more answers for the record
    """

    SHORT_HELP = "Create, retrieve, update, and delete records in a zone"

    def run(self, args):
        # print("record run: %s" % args)
        self._recordAPI = self.nsone.records()
        self._zone = args['ZONE']
        self._domain = args['DOMAIN']
        self._type = args['TYPE']

        # if no dot in the domain name, assume we should add zone
        if self._domain.find('.') == -1:
            self._domain = '%s.%s' % (self._domain, self._zone)

        if args['info']:
            self.info()
        elif args['create']:
            self.create(args)
        elif args['set']:
            self.set(args)
        elif args['answers']:
            self.answers(args)

    def _printRecordModel(self, rdata):
        if self.isTextFormat():
            self.ppText(rdata)
        else:
            self.jsonOut(rdata)

    def create(self, args):
        self.checkWriteLock(args)
        ans = self._recordAPI.getAnswersForBody(args['ANSWER'])
        csubnet = self._getBoolOption(args['--use-client-subnet'])
        out = self._recordAPI.create(self._zone,
                                     self._domain,
                                     self._type,
                                     ans,
                                     ttl=args['--ttl'],
                                     use_csubnet=csubnet)
        self._printRecordModel(out)

    def set(self, args):
        self.checkWriteLock(args)
        csubnet = self._getBoolOption(args['--use-client-subnet'])
        out = self._recordAPI.update(self._zone,
                                     self._domain,
                                     self._type,
                                     ttl=args['--ttl'],
                                     use_csubnet=csubnet)
        self._printRecordModel(out)

    def info(self):
        rdata = self._recordAPI.retrieve(self._zone,
                                         self._domain,
                                         self._type)
        self._printRecordModel(rdata)

    def answers(self, args):
        self.checkWriteLock(args)
        ans = self._recordAPI.getAnswersForBody(args['ANSWER'])
        out = self._recordAPI.update(self._zone,
                                     self._domain,
                                     self._type,
                                     answers=ans)
        self._printRecordModel(out)


record = _record()
