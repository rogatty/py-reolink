# coding: utf-8
"""Base Python Class file for Reolink camera."""
import logging
import requests
import sys
from urllib.parse import urlencode

stdout_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[stdout_handler]
)

_LOGGER = logging.getLogger(__name__)


class PyReolink(object):
    """Base object for Reolink camera."""

    def __init__(self, base_url, username, password):
        """Create a PyReolink object.

        :param username: user email
        :param password: user password

        :returns PyReolink base object
        """
        self.__token = None
        self.__headers = None
        self.__params = None

        self.__base_url = base_url
        # set username and password
        self.__password = password
        self.__username = username
        self.session = requests.Session()

        # login user
        self.login()

    def __repr__(self):
        """Object representation."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.__username)

    def login(self):
        """Login to Reolink."""
        _LOGGER.debug("Creating Reolink session")
        data = self.query(
            {'cmd': 'Login'},
            method='POST',
            body=[
                {
                    'action': 0,
                    'cmd': 'Login',
                    'param': {
                        'User': {
                            'userName': self.__username,
                            'password': self.__password
                        }
                    }
                }
            ])

        data = data[0]

        if isinstance(data, dict) and data.get('code') == 0:
            self.__token = data.get('value').get('Token').get('name')
        else :
            _LOGGER.error("Failed to authenticate")

    def query(self,
              query_params,
              method='GET',
              body=None,
              retry=3):
        """
        Return a JSON object or raw session.

        :param query_params: Dictionary to use as query params
        :param method: Specify the method GET, POST or PUT. Default is GET.
        :param body: Dictionary to be appended on request.body
        :param retry: Attempts to retry a query. Default is 3.
        """
        response = None
        loop = 0

        while loop <= retry:
            headers = {'Content-Type': 'application/json'}

            if self.__token is not None:
                query_params.update({'token': self.__token})

            url = self.__base_url + '/cgi-bin/api.cgi?' + urlencode(query_params)

            _LOGGER.debug("Querying %s on attempt: %s/%s", url, loop, retry)
            _LOGGER.debug("Body: %s", body)
            loop += 1

            # define connection method
            req = None

            if method == 'GET':
                req = self.session.get(url, headers=headers)
            elif method == 'POST':
                req = self.session.post(url, json=body, headers=headers)

            if req and (req.status_code == 200):
                response = req.json()
                break

        _LOGGER.debug("Response: %s", response)

        return response

    def set_ir_lights(self, state):
        """Set IR lights."""
        _LOGGER.debug("Setting IR lights to %s", state)
        data = self.query(
            {'cmd': 'SetIrLights'},
            method='POST',
            body=[
                {
                    'action': 0,
                    'cmd': 'SetIrLights',
                    'param': {
                        'IrLights': {
                            'state': state
                        }
                    }
                }
            ])

        data = data[0]

        if isinstance(data, dict) and data.get('code') == 0:
            _LOGGER.info("Successfully set IR lights to %s", state)
        else:
            _LOGGER.error("Failed to set IR lights", state)


    def goto_ptz_preset(self, preset_id):
        """Go to PTZ preset."""
        _LOGGER.debug("Using PTZ preset with id %s", preset_id)
        data = self.query(
            {'cmd': 'PtzCtrl'},
            method='POST',
            body=[
                {
                    'action': 0,
                    'cmd': 'PtzCtrl',
                    'param': {
                        'channel': 0,
                        'id': preset_id,
                        'op': 'ToPos',
                        'speed': 32
                    }
                }
            ])

        data = data[0]

        if isinstance(data, dict) and data.get('code') == 0:
            _LOGGER.info("Successfully used PTZ preset with id %s", preset_id)
        else:
            _LOGGER.error("Failed to use PTZ preset with id %s", preset_id)

