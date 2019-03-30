# coding: utf-8
"""
Base Python Class file for Reolink camera
Tested with Reolink C1 Pro
"""
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

# Disable logging requested URLs to hide token from logs
logging.getLogger('urllib3').setLevel(logging.WARNING)


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
        return '<{0}: {1}>'.format(self.__class__.__name__, self.__username)

    def login(self):
        """Login to Reolink."""
        _LOGGER.debug('Creating Reolink session')
        data = self.query(
            query_params={'cmd': 'Login'},
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
            ],
            disable_logging=True)

        data = data[0]

        if isinstance(data, dict) and data.get('code') == 0:
            self.__token = data.get('value').get('Token').get('name')
        else:
            _LOGGER.error('Failed to authenticate')

    def get_ir_lights(self):
        """Get IR lights state."""
        _LOGGER.debug('Getting IR lights state')
        data = self.query(
            body=[
                {
                    'action': 1,
                    'cmd': 'GetIrLights',
                }
            ])

        data = data[0]

        if isinstance(data, dict) and data.get('code') == 0:
            state = data.get('value').get('IrLights').get('state')
            _LOGGER.info('Successfully got IR lights state: %s', state)
            return state
        else:
            _LOGGER.error('Failed to get IR lights state')
            return None

    def set_ir_lights(self, state):
        """
        Set IR lights state

        :param state: 'Auto' or 'Off'
        """
        _LOGGER.debug('Setting IR lights state to %s', state)
        data = self.query(
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
            _LOGGER.info('Successfully set IR lights state to %s', state)
        else:
            _LOGGER.error('Failed to set IR lights state', state)

    def goto_ptz_preset(self, preset_id):
        """Go to PTZ preset."""
        _LOGGER.debug('Using PTZ preset with id %s', preset_id)
        data = self.query(
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
            _LOGGER.info('Successfully used PTZ preset with id %s', preset_id)
        else:
            _LOGGER.error('Failed to use PTZ preset with id %s', preset_id)

    def query(self,
              query_params=None,
              method='POST',
              body=None,
              disable_logging=False):
        """
        Return a JSON object or raw session.

        :param query_params: Dictionary to use as query params
        :param method: Specify the method GET or POST
        :param body: Dictionary to be appended to request.body
        :param disable_logging: Disable logging to e.g. hide credentials
        """
        if query_params is None:
            query_params = {}

        parsed_response = None
        retry = 3
        attempt = 1

        if self.__token is not None:
            query_params.update({'token': self.__token})

        headers = {'Content-Type': 'application/json'}
        url = self.__base_url + '/cgi-bin/api.cgi?' + urlencode(query_params)

        while attempt <= retry:
            if not disable_logging:
                _LOGGER.debug('Sending request, attempt: %s/%s', attempt, retry)
                _LOGGER.debug('Body: %s', body)

            attempt += 1
            response = None

            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=body, headers=headers)

            if response and (response.status_code == 200):
                parsed_response = response.json()
                break

            # TODO handle errors, e.g. refresh session when expired

        if not disable_logging:
            _LOGGER.debug('Parsed response: %s', parsed_response)

        return parsed_response
