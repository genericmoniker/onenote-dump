from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session
import datetime
import json
import logging
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

client_id = 'c55c98cc-9cf9-43dc-8e84-38b60cd514b5'
scope = ['Notes.Read']
auth_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'

# Redirect URI registered at:
# https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredAppsPreview
redirect_uri = 'http://localhost:8000/auth'

token_path = Path.home() / '.onenote-dump-token'


def get_session():
    try:
        return session_from_saved_token()
    except (IOError, TokenExpiredError):
        return session_from_user_auth()


def session_from_saved_token():
    token = _load_token()
    expires = datetime.datetime.fromtimestamp(token['expires_at'])
    # If the token will expire in the next few minutes, just get a new one.
    if expires < datetime.datetime.now() + datetime.timedelta(minutes=5):
        logger.debug('Saved token expired.')
        raise TokenExpiredError()
    s = OAuth2Session(client_id, token=token)
    return s


def session_from_user_auth():
    """Get an authenticated session by having the user authorize access."""
    server = AuthHTTPServer(redirect_uri)
    server.start()

    # Give the server a moment to start.
    # More elegant would be to wait until it responds with a 200.
    sleep(3)

    s = OAuth2Session(
        client_id,
        scope=scope,
        redirect_uri=redirect_uri,
        token_updater=_save_token,
    )
    authorization_url, state = s.authorization_url(auth_url)
    logger.info('Launching browser to authorize... %s', authorization_url)
    webbrowser.open(authorization_url)

    redirect_url = server.wait_for_auth_redirect()
    token = s.fetch_token(
        token_url=token_url,
        client_id=client_id,
        authorization_response=redirect_url,
        include_client_id=True,
    )
    _save_token(token)
    return s


class _AuthServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Request received: ' + self.path.encode())
        logger.debug('Queueing %s', self.path)
        self.server.queue.put(self.path)


class AuthHTTPServer:
    """Simple HTTP server to handle the authorization redirect.

    Note that on Windows this will trigger a "Windows Security Alert" and
    prompt the user to allow access through the firewall.
    """

    def __init__(self, url):
        self.url = urlparse(url)
        self.queue = Queue()
        self.server = None

    def start(self):
        """Start the server."""
        thread = Thread(target=self._run_server, name='HTTPServer')
        thread.start()

    def wait_for_auth_redirect(self):
        """Wait for the authorization redirect."""
        path = ''
        while self.url.path not in path:
            path = self.queue.get()
            logger.debug('Received %s', path)
        logger.debug('Matched expected redirect; stopping server.')
        self.server.shutdown()
        return path

    def _run_server(self):
        address = ('', self.url.port)
        self.server = HTTPServer(address, _AuthServerHandler)
        self.server.queue = self.queue
        self.server.serve_forever()


def _save_token(token):
    token_path.write_text(json.dumps(token))
    logger.debug('Auth token saved to %s', token_path)


def _load_token():
    token = json.loads(token_path.read_text())
    logger.debug('Auth token loaded from %s', token_path)
    return token
