"""
Test return status code value?
0: help
1: missing command
"""


# import mock
# import pytest
# from pytest_mock import mocker
# from docopt import docopt, DocoptExit
#
# from ns1cli.commands import zone
# import nsone
# from nsone.zones import Zones
#
# @pytest.fixture()
# def mocked_zone_api(mocker):
#     zArgs = {
#         'list.return_value': {},
#         'retrieve.return_value': {},
#         'create.return_value': {},
#         'delete.return_value': {},
#     }
#     mock_zone_api = mock.MagicMock(spec=Zones, **zArgs)
#
#     mockArgs = {'zones.return_value': mock_zone_api}
#     mock_nsone = mock.MagicMock(spec=nsone, **mockArgs)
#
#     mocker.patch.object(zone, 'nsone', mock_nsone)
#     return mock_zone_api
#
#
# @pytest.mark.parametrize(
#     'args', [
#         ['zone'],
#         ['zone', 'help'],
#         ['zone', 'create'],
#         ['zone', 'delete'],
#         ['zone', 'help', 'list'],
#         ['zone', 'help', 'create'],
#         ['zone', 'help', 'delete'],
#     ]
# )
# def test_cmd_show_help(args):
#     with pytest.raises(DocoptExit):
#         docopt(zone.__doc__, argv=args)
#
#
# @pytest.mark.parametrize(
#     'args, ZONE', [
#         (['zone', 'list'], None),
#     ]
# )
# def test_list_cmd(mocked_zone_api, args, ZONE):
#     args = docopt(zone.__doc__, argv=args)
#     zone.run(args)
#
#     assert zone._zone == ZONE
#     assert mocked_zone_api.list.called
#     mocked_zone_api.list.assert_called_with()
#
# #
# # @pytest.mark.parametrize(
# #     'cmd, subCmd, ZONE, options', [
# #         # ('zone', 'create', 'test.zone', None),
# #         ('zone', 'create', 'test.zone', '--retry', 1)
# #     ]
# # )
# # def test_create_cmd(mocked_zone_api, cmd, subCmd, ZONE, options):
# #
# #     argss = [cmd, subCmd, ZONE, options]
# #     args = docopt(zone.__doc__, argv=argss)
# #     assert args['ZONE'] == ZONE
# #
# #     zone.run(args)
# #
# #     assert zone._zone == ZONE
# #     assert mocked_zone_api.create.called
# #     assert mocked_zone_api.create.call_args == mock.call(ZONE, options)
# #     # mocked_zone_api.create.assert_called_with(exp_zone, exp_options)
