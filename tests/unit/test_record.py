import mock
import pytest
from pytest_mock import mocker
from docopt import docopt, DocoptExit

from ns1cli.commands.base import CommandException
from ns1cli.commands import record
import nsone
from nsone.records import Records

try:  # Python 2
    from itertools import izip as zip
except ImportError:
    pass


@pytest.fixture()
def mocked_record_api(mocker):
    # Mock nsone api client record resource
    rArgs = {
        'list.return_value': {},
        'retrieve.return_value': {},
        'create.return_value': {},
        'delete.return_value': {},
        'update.return_value': {},
    }
    mock_record_api = mock.MagicMock(spec=Records, **rArgs)

    # Mocks nsone api client
    mockArgs = {
        'records.return_value': mock_record_api,
        'config.isKeyWriteLocked.return_value': False
    }
    mock_nsone = mock.MagicMock(spec=nsone, **mockArgs)

    mocker.patch.object(record, 'nsone', mock_nsone)

    # Return the mocked RECORD api client resource
    return mock_record_api


@pytest.mark.parametrize(
    'args', [['record'],
             ['record', 'help'],
             ['record', 'info'],
             ['record', 'create'],
             ['record', 'set'],
             ['record', 'meta', 'set'],
             ['record', 'meta', 'remove'],
             ['record', 'help', 'list'],
             ['record', 'help', 'info'],
             ['record', 'help', 'create']]
)
def test_cmd_show_help(args):
    with pytest.raises(DocoptExit):
        docopt(record.__doc__, argv=args)

@pytest.mark.parametrize(
    'args', [
        ['record', 'create', 'test.com', 'mail', 'MX', '--priority', '10', '1.2.3.4'],
        ['record', 'answer', '', 'mail', 'MX', '--priority', '10', '1.2.3.4'],
    ]
)
def test_info_cmd(mocked_record_api):
    cmd, subCmd, zone = 'record', 'info', 'test.zone'
    args = docopt(record.__doc__, argv=[cmd, subCmd])

    record.run(args)

    assert record._zone is None
    assert mocked_record_api.list.called
    assert mocked_record_api.list.call_args == mock.call()


# def test_info_cmd(mocked_record_api):
#     cmd, subCmd, name = 'record', 'info', 'test.zone'
#     args = docopt(record.__doc__, argv=[cmd, subCmd, name])
#     assert args['ZONE'] == name
#
#     record.run(args)
#
#     assert record._zone == name
#     assert mocked_record_api.retrieve.called
#     assert mocked_record_api.retrieve.call_args == mock.call(name)


# Implemented Options
# OPTIONS = ['retry', 'refresh', 'expiry', 'nx_ttl', 'link']
#PASSTHRU_FIELDS = ['secondary', 'hostmaster', 'meta', 'networks', 'link']


# def pairwise(iterable):
#     "s -> (s0, s1), (s2, s3), (s4, s5), ..."
#     a = iter(iterable)
#     return zip(a, a)
#

# @pytest.mark.parametrize(
#     'options', [['--link', 'test.zone'],
#                 ['--expiry', 1],
#                 ['--expiry', 1, '--nx_ttl', 1],
#                 ['--expiry', 1, '--nx_ttl', 1, '--refresh', 1],
#                 ['--expiry', 1, '--nx_ttl', 1, '--refresh', 1, '--retry', 1],
#                 ['--expiry', 1, '--nx_ttl', 1, '--refresh', 1, '--retry', 1, '--link', 'test.zone']]
# )
# def test_create_cmd(mocked_zone_api, options):
#     cmd, subCmd, name = 'zone', 'create', 'test.zone'
#     args = docopt(zone.__doc__, argv=[cmd, subCmd, name] + options)
#     assert args['ZONE'] == name
#
#     zone.run(args)
#
#     assert zone._zone == name
#     assert mocked_zone_api.create.called
#
#     # Format options as kwargs that nsone api client expects.
#     api_options = {opt.lstrip('--'): val for opt, val in pairwise(options)}
#     assert mocked_zone_api.create.call_args == mock.call(name, **api_options)
#
#
# def test_delete_cmd(mocked_zone_api):
#     cmd, subCmd, name, force = 'zone', 'delete', 'test.zone', '-f'
#     args = docopt(zone.__doc__, argv=[cmd, subCmd, name, force])
#     assert args['ZONE'] == name
#
#     zone.run(args)
#
#     assert zone._zone == name
#     assert mocked_zone_api.delete.called
#     assert mocked_zone_api.delete.call_args == mock.call(name)


# @pytest.mark.parametrize(
#     'cmd, subCmd, name', [['zone', 'create', 'test.zone'],
#                           ['zone', 'delete', 'test.zone']]
# )
# def test_writelock(mocked_zone_api, cmd, subCmd, name):
#     args = docopt(zone.__doc__, argv=[cmd, subCmd, name])
#
#     # Lock the key
#     zone.nsone.config.isKeyWriteLocked.return_value = True
#     with pytest.raises(CommandException):
#         args = docopt(zone.__doc__, argv=[cmd, subCmd, name])
#
#     args = docopt(zone.__doc__, argv=[cmd, subCmd, name, '-f'])
