import mock
import pytest
from pytest_mock import mocker
from docopt import docopt, DocoptExit

from ns1cli.commands.base import CommandException
from ns1cli.commands import zone
import nsone
from nsone.zones import Zones

try:  # Python 2
    from itertools import izip as zip
except ImportError:
    pass


@pytest.fixture()
def mocked_zone_api(mocker):
    # Mock nsone api client zone resource
    zArgs = {
        'list.return_value': {},
        'retrieve.return_value': {},
        'create.return_value': {},
        'update.return_value': {},
        'delete.return_value': {},
    }
    mock_zone_api = mock.MagicMock(spec=Zones, **zArgs)

    # Mocks nsone api client
    mockArgs = {
        'zones.return_value': mock_zone_api,
        'config.isKeyWriteLocked.return_value': False
    }
    mock_nsone = mock.MagicMock(spec=nsone, **mockArgs)

    mocker.patch.object(zone, 'nsone', mock_nsone)

    # Return the mocked ZONE api client resource
    return mock_zone_api


@pytest.mark.parametrize(
    'args', [['zone'],
             ['zone', 'help'],
             ['zone', 'create'],
             ['zone', 'delete'],
             ['zone', 'help', 'list'],
             ['zone', 'help', 'create'],
             ['zone', 'help', 'delete']]
)
def test_cmd_show_help(args):
    with pytest.raises(DocoptExit):
        docopt(zone.__doc__, argv=args)


def test_list_cmd(mocked_zone_api):
    cmd, subCmd = 'zone', 'list'
    args = docopt(zone.__doc__, argv=[cmd, subCmd])

    zone.run(args)

    assert zone._zone is None
    assert mocked_zone_api.list.called
    assert mocked_zone_api.list.call_args == mock.call()


def test_info_cmd(mocked_zone_api):
    cmd, subCmd, name = 'zone', 'info', 'test.zone'
    args = docopt(zone.__doc__, argv=[cmd, subCmd, name])
    assert args['ZONE'] == name

    zone.run(args)

    assert zone._zone == name
    assert mocked_zone_api.retrieve.called
    assert mocked_zone_api.retrieve.call_args == mock.call(name)


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


@pytest.mark.parametrize(
    'options', [['--link', 'test.zone'],
                ['--expiry', 1],
                ['--expiry', 1, '--nx_ttl', 1],
                ['--expiry', 1, '--nx_ttl', 1, '--refresh', 1],
                ['--expiry', 1, '--nx_ttl', 1, '--refresh', 1, '--retry', 1],
                ['--expiry', 1, '--nx_ttl', 1, '--refresh', 1, '--retry', 1,
                 '--link', 'test.zone']]
)
def test_create_cmd(mocked_zone_api, options):
    cmd, subCmd, name = 'zone', 'create', 'test.zone'
    args = docopt(zone.__doc__, argv=[cmd, subCmd, name] + options)
    assert args['ZONE'] == name

    zone.run(args)

    assert zone._zone == name
    assert mocked_zone_api.create.called

    # Format options as kwargs that nsone api client expects.
    api_options = {opt.lstrip('--'): val for opt, val in pairwise(options)}
    assert mocked_zone_api.create.call_args == mock.call(name, **api_options)


def test_delete_cmd(mocked_zone_api):
    cmd, subCmd, name, force = 'zone', 'delete', 'test.zone', '-f'
    args = docopt(zone.__doc__, argv=[cmd, subCmd, name, force])
    assert args['ZONE'] == name

    zone.run(args)

    assert zone._zone == name
    assert mocked_zone_api.delete.called
    assert mocked_zone_api.delete.call_args == mock.call(name)
