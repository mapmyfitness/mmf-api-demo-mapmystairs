"""
    MapMyFitness API
    ~~~~~~~~~~~~~~~~
"""
import requests
from requests_oauthlib import OAuth1
import time
from urlparse import parse_qs


class MapMyFitnessAPI:
    """
    Main API Class to handle talking to the MapMyFitness API
    See: https://developer.mapmyapi.com/docs
    """
    
    API_VERSION = "v7.0"
    API_URL = "https://api.mapmyapi.com/" + API_VERSION
    
    # API_URL = "https://api.mapmyapi.com/api/0.2"
    
    def __init__(self, client_key, client_secret,
                 token_key=None, token_secret=None):
        """
        Initialization
        
        :param str client_key: Client API Key
        :param str client_secret: Client API Key Secret
        :optparam str token_key: Requestor Token
        :optparam str token_secret: Requestor Token Secret
        
        """
        self.client_key = client_key
        self.client_secret = client_secret
        self.token_key = token_key
        self.token_secret = token_secret          

    def call(self, method, http_method="GET", params=None, data=None):
        """
        Make an API Call
        
        :param str method: Path to API Method
        :param dict params: Dictionary of Key/Value parameters
        """
        
        # check if api version passed
        if self.API_VERSION in method:
            method = method.replace("/" + self.API_VERSION, "")
        
        # get data 
        url = self.API_URL + method
        
        oauth = OAuth1(self.client_key, client_secret=self.client_secret, 
                       resource_owner_key=self.token_key,
                       resource_owner_secret=self.token_secret,
                       signature_type='AUTH_HEADER')
        
        headers = {"Accept-Encoding": "gzip", "Accept": "application/json"}
        
        if http_method == "GET":
            r = requests.get(url=url, params=params, auth=oauth,
                             headers=headers)
        elif http_method == "POST":
            r = requests.post(url=url, params=params, auth=oauth,
                             data=data, headers=headers)
        
        return r.json()

    def get_temporary_credentials(self, callback_uri=None):
        """
        Get temporary credentials
        
        :param str callback_uri: Callback URI
        """
        url = self.API_URL + "/oauth/temporary_credential/"
        
        # Build Oauth Request
        oauth = OAuth1(self.client_key, client_secret=self.client_secret,
                       callback_uri=callback_uri, signature_type='AUTH_HEADER')
        
        # Send Request
        r = requests.post(url=url,
                 headers={'Content-Type': 'application/x-www-form-urlencoded',
                          'Accept': 'application/x-www-form-urlencoded'},
                 auth=oauth)

        return parse_qs(r.content)
    
    def get_token_credentials(self, verifier):
        """
        Exchange the temporary credentials and authorization 
        verifier for token credentials.
        
        :param str verifier: Oauth Verifier
        """
        url = self.API_URL + "/oauth/token_credential/"
        
        oauth = OAuth1(self.client_key, client_secret=self.client_secret, 
                       resource_owner_key=self.token_key,
                       resource_owner_secret=self.token_secret,
                       verifier=verifier)
    
        r = requests.post(url=url, 
                headers={'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/x-www-form-urlencoded'},
                auth=oauth)
        
        return parse_qs(r.content)
    