#
# Copyright (c) 2014 NSONE, Inc.
#
# License under The MIT License (MIT). See LICENSE in project root.
#

from .base import BaseCommand


class _record(BaseCommand):

    """
    usage: nsone record info ZONE DOMAIN TYPE
           nsone record create ZONE DOMAIN TYPE [options] (ANSWER ...)
           nsone record set ZONE DOMAIN TYPE options
           nsone record meta set ZONE DOMAIN TYPE KEY VALUE
           nsone record meta remove ZONE DOMAIN TYPE KEY VALUE
           nsone record answers ZONE DOMAIN TYPE [options] (ANSWER ...)
           nsone record answer add ZONE DOMAIN TYPE ANSWER
           nsone record answer remove ZONE DOMAIN TYPE ANSWER
           nsone record answer meta set ZONE DOMAIN TYPE ANSWER KEY VALUE
           nsone record answer meta remove ZONE DOMAIN TYPE ANSWER KEY

    Record operations. You may leave the zone name off of DOMAIN (do not end it
    with a period)

    Options:
       --ttl N                          TTL (Defaults to default zone TTL)
       --use-client-subnet BOOL         Set use of client-subnet EDNS option
                                        (Defaults to True on new records)
       --priority                       For MX records, the priority
       -f                               Force: override the write lock if one
                                        exists

    Record Actions:
       info          Get record details
       create        Create a new record, optionally with simple answers
       set           Set record properties, including record level meta data
       answers       Set one or more simple answers (no meta) for the record
       meta set      Set record level meta data
       meta remove   Remove record level meta data

    Answer Actions:
       add           Add an answer to a record
       remove        Remove an answer from a record
       meta set      Set meta data key/value to an answer. If it doesn't exist
                     it will be added
       meta remove   Remove meta data key from an answer

    Examples:
       record create test.com mail MX --priority 10 1.2.3.4
       record answer add test.com mail MX --priority 20 2.3.4.5

       record create test.com geo A --ttl 300 --use-client-subnet true
       record answers test.com geo A --ttl 300 1.2.3.4 6.7.8.9
       record answer add test.com geo A 3.3.3.3
       record answer meta set test.com geo A 1.2.3.4 georegion US-WEST
       record answer meta set test.com geo A 6.7.8.9 georegion US-EAST
       record answer meta set test.com geo A 3.3.3.3 georegion US-CENTRAL
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

        # order matters
        if args['info']:
            self.info()
        elif args['meta'] and args['answer']:
            self.answer_meta(args)
        elif args['answer']:
            self.answer(args)
        elif args['meta']:
            self.record_meta(args)
        elif args['create']:
            self.create(args)
        elif args['set']:
            self.set(args)
        elif args['set-answers']:
            self.set_answers(args)

    def _printRecordModel(self, rdata):
        if self.isTextFormat():
            self.ppText(rdata)
        else:
            self.jsonOut(rdata)

    def create(self, args):
        self.checkWriteLock(args)
        csubnet = self._getBoolOption(args['--use-client-subnet'])
        # XXX handle mx priority
        out = self._recordAPI.create(self._zone,
                                     self._domain,
                                     self._type,
                                     args['ANSWER'],
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

    def set_answers(self, args):
        self.checkWriteLock(args)
        # XXX handle mx priority
        out = self._recordAPI.update(self._zone,
                                     self._domain,
                                     self._type,
                                     answers=args['ANSWER'])
        self._printRecordModel(out)


record = _record()
