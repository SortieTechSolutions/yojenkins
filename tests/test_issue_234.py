"""Test that browser commands skip auth when a full URL is provided (issue #234)"""

from unittest.mock import patch, MagicMock


class TestJobBrowserSkipsAuth:
    @patch('yojenkins.cli.cli_job.browser_open')
    @patch('yojenkins.cli.cli_job.cu.is_full_url', return_value=True)
    @patch('yojenkins.cli.cli_job.cu.config_yo_jenkins')
    def test_job_browser_url_skips_auth(self, mock_config, mock_is_url, mock_browser):
        from yojenkins.cli import cli_job
        cli_job.browser(profile=None, token=None, job='http://jenkins/job/foo')
        mock_browser.assert_called_once_with('http://jenkins/job/foo')
        mock_config.assert_not_called()


class TestFolderBrowserSkipsAuth:
    @patch('yojenkins.cli.cli_folder.browser_open')
    @patch('yojenkins.cli.cli_folder.cu.is_full_url', return_value=True)
    @patch('yojenkins.cli.cli_folder.cu.config_yo_jenkins')
    def test_folder_browser_url_skips_auth(self, mock_config, mock_is_url, mock_browser):
        from yojenkins.cli import cli_folder
        cli_folder.browser(profile=None, token=None, folder='http://jenkins/job/folder1')
        mock_browser.assert_called_once_with('http://jenkins/job/folder1')
        mock_config.assert_not_called()
