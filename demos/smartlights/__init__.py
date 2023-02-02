import requests 

class SmartLights(object):
    '''
    A class to control the SmartLights Website through a REST API

    key identifies the unqiue SmartLights page
    '''
    def __init__(self, key=""):
        self._key = key
        self._endpoint = "https://smartlights.ist256.com/"
        self._headers = { "X-key" : self._key }

    def _httpget(self, url):
        response = requests.get(url, headers=self._headers, timeout=5)
        response.raise_for_status()
        return response.json()

    def status(self, index = None):
        '''
        Returns the status of all lights or a single light at the given index
        '''
        if index is None:
            url = f"{self._endpoint}lights/status"
            lights = self._httpget(url)
            return lights
        else:
            url = f"{self._endpoint}light/{index}/status"
            light = self._httpget(url)
            return light

    def on(self, index = None):
        '''
        Turns on all lights or a single light at the given index
        '''
        if index is None:
            url = f"{self._endpoint}lights/on"
            lights = self._httpget(url)
            return lights
        else:
            url = f"{self._endpoint}light/{index}/on"
            light = self._httpget(url)
            return light

    def off(self, index = None):
        '''
        Turns off all lights or a single light at the given index
        '''
        if index is None:
            url = f"{self._endpoint}lights/off"
            lights = self._httpget(url)
            return lights
        else:
            url = f"{self._endpoint}light/{index}/off"
            light = self._httpget(url)
            return light
