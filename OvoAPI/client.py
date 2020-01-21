# -*- coding: utf-8 -*-
from io import BytesIO
import logging
import gzip
import json
import os
import uuid
import requests
import string
import random
import time

from .constant import Constant


from .utils import *
logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, phone_number, OVODataPath=None, **kwargs):
        """
        :param kwargs: See below
        :Keyword Arguments:
            - **timeout**: Timeout interval in seconds. Default: 15
            - **api_url**: Override the default api url base
        :return:
        """

        self.phone_number = None
        self.timeout = kwargs.pop('timeout', 15)
        self.logger = logger
        self.settings = None
        self.uuid = None  # // UUID
        self.isLoggedIn = False
        self.token = None  # // _csrftoken
        self.OVODataPath = None
        self.customPath = False

        if OVODataPath is not None:
            self.OVODataPath = OVODataPath
            self.customPath = True
        else:
            self.OVODataPath = os.path.join(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'),
                phone_number,
                ''
            )
            if not os.path.isdir(self.OVODataPath):
                os.mkdir(self.OVODataPath, 0o777)
        
        self.checkSettings(phone_number)
        self.setUser(phone_number)
    

        super(Client, self).__init__()
    

    def setUser(self, phone_number):
        """
        Set the user. Manage multiple accounts.
        :type phone_number: str
        :param phone_number: Your Instagram phone_number.
        :
        """
        self.phone_number = phone_number

        self.checkSettings(phone_number)

        if os.path.isfile(self.OVODataPath + 'settings-'+ self.phone_number + '.dat') and \
                (self.settings.get('access_token') != None):
            self.token = self.settings.get('access_token')
            self.uuid = self.settings.get('uuid')
        else:
            self.isLoggedIn = False

    def login(self, force=False):
        response = None
        if (not self.isLoggedIn) or force:
            self.uuid = str(uuid.uuid4())
            self.settings.set('uuid', str(self.uuid))

            data = {
                "deviceId": self.uuid,
                "deviceName": "iPhone12,3",
                "location": "Jakarta",
                "mobile": self.phone_number
            }

            response = self._call_api('/api/auth/customer/login2FA', params=data, version="v2.0", method="POST")

            return response
        else:
            return 'user has been logged in.'



    def verify(self, otp, ref_id):
        if (not self.isLoggedIn):
            lettersAndDigits = string.ascii_letters + string.digits
            data = {
                "deviceId": self.settings.get('uuid'),
                "osVersion": Constant.OS_VERSION,
                "pushNotificationId": ''.join(random.choice(lettersAndDigits) for i in range(64)),
                "osName": "ios",
                "verificationCode": otp,
                "appVersion": Constant.APP_VERSION,
                "refId": ref_id,
                "mobile": self.phone_number
            }

            response = self._call_api('/api/auth/customer/login2FA/verify', params=data, version="v2.0", method="POST")

            return response
            
        else:
            return 'user has been logged in.'

    def verify_security_code(self, security_code, update_access_token):
        if (not self.isLoggedIn):
            
            data = {
                "securityCode": security_code,
                "updateAccessToken": update_access_token,
                "deviceUnixtime": int(time.time())
            }

            response = self._call_api('/api/auth/customer/loginSecurityCode/verify', params=data, version="v2.0", method="POST")

            if response['token']:
                self.isLoggedIn = True
                self.settings.set('access_token', response['token'])
                self.settings.set('email', response['email'])
                self.settings.set('name', response['fullName'])
                return response
            else:
                return response
            
        else:
            return 'user has been logged in.'
    

    def checkSettings(self, phone_number):
        if not self.customPath:
            self.OVODataPath = os.path.join(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'),
                phone_number,
                ''
            )

        if not os.path.isdir(self.OVODataPath): os.mkdir(self.OVODataPath, 0o777)

        self.settings = Settings(
            os.path.join(self.OVODataPath, 'settings-' + phone_number + '.dat')
        )
    @property
    def default_headers(self):
        return {
            'app-id': Constant.APP_ID,
            'accept': '*/*',
            'User-Agent': Constant.USER_AGENT,
            'accept-encoding': 'gzip;q=1.0, compress;q=0.5',
            'accept-language': 'en-ID;q=1.0',
            'os': Constant.OS,
            'app-version': Constant.APP_VERSION
        }


    def _call_api(self, endpoint, params=None, return_response=False, version="", method="GET"):
        """
        Calls the private api.
        :param endpoint: endpoint path that should end with '/', example 'discover/explore/'
        :param params: POST parameters
        :param query: GET url query parameters
        :param return_response: return the response instead of the parsed json object
        :param version: for the versioned api base url. Default 'v1'.
        :param method
        :return:
        """
        if version:
            version = '/' + version

        url = "{0}{1}".format(Constant.API_BASE_URL.format(version=version), endpoint)


        headers = self.default_headers
        response = None

        if (self.settings.get('access_token')):
            headers['authorization'] = 'Bearer ' + self.settings.get('access_token')

        if (method == 'POST'):
            response = requests.post(url, json=params, headers=headers)
        else:
            response = requests.get(url, params=params, headers=headers)



        json_response = response.json()

        print("url: " + url)
        return json_response