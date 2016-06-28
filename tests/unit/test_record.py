import pytest
from pytest_mock import mocker
from docopt import docopt, DocoptExit

from ns1cli.commands import record
import nsone
from nsone.records import Records

try:  # Python 2
    from itertools import izip as zip
except ImportError:
    pass

try:  # Python 3.3 +
    import unittest.mock as mock
except ImportError:
    import mock


@pytest.fixture()
def mocked_record_api(mocker):
    # Mock nsone api client record resource
    rArgs = {
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
    'cli_raw_input, exp_call', [
        ['record create test.com mail MX --priority 10 1.2.3.4', 'create'],
        ['record answer add test.com mail MX --priority 20 2.3.4.5', 'answer'],
        ['record create test.com geo A --ttl 300 --use-client-subnet true 1.1.1.1', 'create'],
        ['record meta set test.com geo A priority 5', 'record_meta'],
        ['record answers test.com geo A --ttl 300 1.2.3.4 6.7.8.9', 'set_answers'],
        ['record answer add test.com geo A 3.3.3.3', 'answer'],
        ['record answer meta set test.com geo A 1.2.3.4 georegion US-WEST', 'answer_meta'],
    ]
)
def test_ordering(mocked_record_api, cli_raw_input, exp_call):
    with mock.patch.object(record, exp_call) as mocked_call:
        cli_input = cli_raw_input.split(' ')
        args = docopt(record.__doc__, argv=cli_input)

        record.run(args)
        assert mocked_call.called

# @pytest.mark.parametrize(
#     'args', [
#         ['create', 'test.com', 'mail', 'MX', '--priority', '10', '1.2.3.4'],
#         ['answer', '', 'mail', 'MX', '--priority', '10', '1.2.3.4'],
#     ]
# )
# def test_info_cmd(mocked_record_api, args):
#     cmd, subCmd, zone = 'record', 'info', 'test.zone'
#     args = docopt(record.__doc__, argv=[cmd, subCmd])
#
#     record.run(args)
#
#     assert record._zone is None
#     assert mocked_record_api.retrieve.called
#     assert mocked_record_api.retrieve.call_args == mock.call()
