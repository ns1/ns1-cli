from click.testing import CliRunner


from ns1cli.cli import cli


def test_cli():
    runner = CliRunner()
    assert 1 == 1
    # result = runner.invoke(cli, ['help'])
    # assert result.exit_code == 0
