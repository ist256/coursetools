import datetime 
import os
import json

class Settings(object):
    
    __SETTINGS_FILE = '.settings'
    
    def __init__(self):
        pass 
        
    def load(self):
        if os.path.exists(self.__SETTINGS_FILE):
            with open(self.__SETTINGS_FILE,"r") as f:
                settings = json.load(f)
                return settings
        else:
            return {}
                
    def save(self, settings):
        with open(self.__SETTINGS_FILE,"w") as f:
            json.dump(settings,f)
            return 