"""Regression test for issue #217: YOJENKINS_TOKEN env var must reach auth verify"""

from unittest.mock import MagicMock, patch


class TestAuthVerifyToken:
    """Verify that the token parameter flows through to create_auth()"""

    @patch('click.secho')
    @patch('yojenkins.cli.cli_auth.Auth')
    @patch('yojenkins.cli.cli_auth.Rest')
    def test_verify_passes_token_to_create_auth(self, mock_rest_cls, mock_auth_cls, mock_secho):
        from yojenkins.cli import cli_auth

        mock_auth = MagicMock()
        mock_auth_cls.return_value = mock_auth

        cli_auth.verify(profile='default', token='my-env-token')
        mock_auth.get_credentials.assert_called_once_with('default')
        mock_auth.create_auth.assert_called_once_with(token='my-env-token')

    @patch('click.secho')
    @patch('yojenkins.cli.cli_auth.Auth')
    @patch('yojenkins.cli.cli_auth.Rest')
    def test_verify_passes_none_token_when_not_set(self, mock_rest_cls, mock_auth_cls, mock_secho):
        from yojenkins.cli import cli_auth

        mock_auth = MagicMock()
        mock_auth_cls.return_value = mock_auth

        cli_auth.verify(profile='default', token=None)
        mock_auth.create_auth.assert_called_once_with(token=None)
