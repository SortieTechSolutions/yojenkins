"""Thin wrapper over DockerJenkinsServer for test lifecycle management."""

import logging
import time

import requests

from yojenkins.docker_container.docker_jenkins_server import DockerJenkinsServer

logger = logging.getLogger(__name__)

STARTUP_TIMEOUT_SECONDS = 180
HEALTH_POLL_INTERVAL_SECONDS = 3


class JenkinsTestServer:
    """Manages a Docker Jenkins instance for integration tests.

    Wraps DockerJenkinsServer with:
    - Health-check polling until Jenkins API is ready
    - State reset between test modules
    - Credential/token helpers for test auth
    """

    def __init__(
        self,
        port: int = 9090,
        admin_user: str = 'admin',
        admin_password: str = 'admin',
        container_name: str = 'yojenkins-test-jenkins',
        image_fullname: str = 'yojenkins-test-jenkins:latest',
    ):
        self.port = port
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.server_url = f'http://localhost:{port}'
        self._api_token = None

        self._docker_server = DockerJenkinsServer(
            port=port,
            admin_user=admin_user,
            password=admin_password,
            container_name=container_name,
            image_fullname=image_fullname,
            new_volume=True,
            new_volume_name=f'{container_name}-vol',
        )

    def setup(self):
        """Start the Docker Jenkins container and wait until the API is ready."""
        logger.info('Starting Jenkins test server on %s ...', self.server_url)

        self._docker_server.docker_client_init()
        result = self._docker_server.setup()
        if not result:
            raise RuntimeError('DockerJenkinsServer.setup() failed')

        self._wait_for_ready()
        logger.info('Jenkins test server is ready at %s', self.server_url)

    def _wait_for_ready(self):
        """Poll Jenkins API until it responds with HTTP 200."""
        api_url = f'{self.server_url}/api/json'
        deadline = time.time() + STARTUP_TIMEOUT_SECONDS

        while time.time() < deadline:
            try:
                resp = requests.get(
                    api_url,
                    auth=(self.admin_user, self.admin_password),
                    timeout=5,
                )
                if resp.status_code == 200:
                    logger.info('Jenkins API responded with 200')
                    return
                logger.debug('Jenkins API returned %d, retrying...', resp.status_code)
            except requests.ConnectionError:
                logger.debug('Jenkins not yet reachable, retrying...')

            time.sleep(HEALTH_POLL_INTERVAL_SECONDS)

        raise TimeoutError(f'Jenkins did not become ready within {STARTUP_TIMEOUT_SECONDS}s at {api_url}')

    def get_api_token(self) -> str:
        """Generate or return a cached API token for the admin user."""
        if self._api_token:
            return self._api_token

        # Use Jenkins crumb + API to generate a token
        crumb_url = f'{self.server_url}/crumbIssuer/api/json'
        token_url = f'{self.server_url}/user/{self.admin_user}/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken'
        auth = (self.admin_user, self.admin_password)

        # Get crumb for CSRF
        crumb_resp = requests.get(crumb_url, auth=auth, timeout=10)
        if crumb_resp.status_code != 200:
            raise RuntimeError(f'Failed to get Jenkins crumb: HTTP {crumb_resp.status_code}')
        crumb_data = crumb_resp.json()
        crumb_header = {crumb_data['crumbRequestField']: crumb_data['crumb']}

        # Generate token
        token_resp = requests.post(
            token_url,
            auth=auth,
            headers=crumb_header,
            data={'newTokenName': 'test-api-token'},
            timeout=10,
        )
        if token_resp.status_code != 200:
            raise RuntimeError(f'Failed to generate API token: HTTP {token_resp.status_code}')

        self._api_token = token_resp.json()['data']['tokenValue']
        logger.info("Generated API token for user '%s'", self.admin_user)
        return self._api_token

    def reset_state(self):
        """Delete all jobs created during tests, preserving base JCasC config."""
        logger.info('Resetting Jenkins test server state...')
        api_url = f'{self.server_url}/api/json?tree=jobs[name]'
        auth = (self.admin_user, self.admin_password)

        try:
            resp = requests.get(api_url, auth=auth, timeout=10)
            if resp.status_code != 200:
                logger.warning('Failed to list jobs for reset: HTTP %d', resp.status_code)
                return

            # Get crumb for delete operations
            crumb_url = f'{self.server_url}/crumbIssuer/api/json'
            crumb_resp = requests.get(crumb_url, auth=auth, timeout=10)
            crumb_data = crumb_resp.json()
            crumb_header = {crumb_data['crumbRequestField']: crumb_data['crumb']}

            for job in resp.json().get('jobs', []):
                job_name = job['name']
                delete_url = f'{self.server_url}/job/{job_name}/doDelete'
                requests.post(delete_url, auth=auth, headers=crumb_header, timeout=10)
                logger.debug('Deleted job: %s', job_name)

        except requests.ConnectionError:
            logger.warning('Jenkins not reachable during reset_state, skipping')

    def clean(self):
        """Stop and remove the Docker Jenkins container."""
        logger.info('Cleaning up Jenkins test server...')
        self._docker_server.clean(remove_volume=True)
