from .nbenvironment import NbEnvironment
import pandas as pd
import os

import logging

class Journal:
    
    
    def __init__(self,debug=False):
               
        try:
            self.env = NbEnvironment()
        except S3Error as e:
            print(f"ERROR: Likely cause: File is not in a course folder.")
            raise e
        except Exception as e:
            print(e)
            raise e
                        
    @property
    def properties(self):
        return self.env.properties
        
    
    def __get_path(self, netid = None):
        if netid == None: netid = self.env.netid            
        return f"journal/{netid}.csv"

    def init(self, netid = None):
        tmp = "_tmp.csv"
        journal_path = self.__get_path(netid)
        
        logging.debug(f"CMD: init_journal netid={netid}, journal_path={journal_path}")
        dataframe = pd.DataFrame( { 'Date' : [], 'Hours' : [], 'Comments' : [] } )
        dataframe.to_csv(tmp,index=False)
        response = self.env.mc.put(self.env.bucket,tmp,journal_path,)
        os.remove(tmp)
        logging.debug("DONE: init_journal")
        return dataframe
    
    def load(self, netid = None):
        
        journal_path = self.__get_path(netid)
        
        logging.debug(f"CMD: load_journal netid={netid}, journal_path={journal_path}")
        
        #try:
        dataframe = pd.read_csv(self.env.mc.get(self.env.bucket, journal_path))
        #except: # ugh, bad coding here....
            #dataframe = self.init(netid)
            #pass
           
        return dataframe
    
    def save(self, dataframe, netid = None):
        tmp = "_tmp.csv"
        journal_path = self.__get_path(netid)
        
        logging.debug(f"CMD: save_journal bucket={self.env.bucket} netid={netid}, journal_path={journal_path}")
        dataframe.to_csv(tmp,index=False)
        result = self.env.mc.fput(self.env.bucket,tmp,journal_path)
        os.remove(tmp)

        return result
