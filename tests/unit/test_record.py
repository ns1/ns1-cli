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
