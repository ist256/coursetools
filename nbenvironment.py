import os 
import ipykernel
import requests 
import json
import datetime
from datetime import datetime, timezone
import time
import pandas as pd
from .minioclient import MinioClient
from .settings import Settings
import urllib.parse

class NbEnvironment(object):
    
    version = "20221111a"
    
    def __init__(self, lesson = None, filename = None):

        # compositions
        self.__minio_client = MinioClient()
        self.__settings = Settings().load()

        
        # properties
        self.__netid = self.__find_netid()
        self.__notebook_path = self.__find_notebook_path()
        self.__service_prefix = self.__find_service_prefix()
        self.__course = self.__find_course()
        self.__git_folder = self.__find_git_folder()
        self.__bucket = self.__find_bucket()
        self.__filename = self.__find_filename() if filename == None else filename
        self.__lesson = self.__find_lesson() if lesson == None else lesson 
        self.__filespec = self.__find_filespec()
        self.__run_datetime = self.to_datetime_string(datetime.now())
        
        # timezone
        self.__set_timezone("America/New_York")

        # roster and assigments
        self.__roster_df = self.__load_roster()
        self.__assignments_df = self.__load_assignments()
        
        self.__is_student = self.__find_student_netid_on_roster()
        self.__is_instructor = self.__find_instructor_netid_on_roster()
        self.__instructor_netid = self.__find_instructor_by_student()
        
        self.__assignment = self.__find_assignment()
        self.__is_assignment = False if self.__assignment == {} else True
        self.__assignment_target_file = self.__generate_assignment_target_file()
            

    def __load_roster(self):
        roster_url='metadata/roster.csv'
        if self.__minio_client.get_info(self.__bucket, roster_url ) != None:
            data = self.__minio_client.get(self.__bucket, roster_url )
            roster = pd.read_csv(data)
            # check columns student_netid instructor_netid ???
            return roster
        else:
            return pd.DataFrame()

    def __load_assignments(self):
        assignments_url='metadata/assignments.csv'
        if self.__minio_client.get_info(self.__bucket, assignments_url ) != None:
            data = self.__minio_client.get(self.__bucket, assignments_url )
            assignments = pd.read_csv(data)
            return assignments
        else:
            return pd.DataFrame()

    def __set_timezone(self, tz_string):
        self.__timezone = tz_string
        os.environ['TZ'] = self.__timezone
        time.tzset()
        

    @property
    def properties(self):
        '''
        Return all properties as a dictionary
        '''
        tmp = {}
        for key in self.__dict__.keys():
            if not key.endswith("_df"):
                tmp[key.replace('_NbEnvironment__','')] = self.__dict__[key]
        return tmp
    
    @property
    def assignment_target_file(self):
        return self.__assignment_target_file
    
    @property
    def assignment(self):
        return self.__assignment
    
    @property
    def is_assignment(self):
        return self.__is_assignment
    
    @property
    def instructor_netid(self):
        return self.__instructor_netid

    @property
    def is_instructor(self):
        return self.__is_instructor
    
    @property
    def is_student(self):
        return self.__is_student
    @property
    def timezone(self):
        return self.__timezone
    
    @property 
    def settings(self):
        return self.__settings
    
    @property 
    def netid(self):
        return self.__netid

    @property 
    def notebook_path(self):
        return self.__notebook_path

    @property 
    def service_prefix(self):
        return self.__service_prefix
    
    @property 
    def course(self):
        return self.__course
    
    @property 
    def git_folder(self):
        return self.__git_folder
    
    @property 
    def bucket(self):
        return self.__bucket
    
    @property
    def filename(self):
        return self.__filename
    
    @property
    def lesson(self):
        return self.__lesson
    
    @property
    def filespec(self):
        return self.__filespec
    
    @property 
    def run_datetime(self):
        return self.__run_datetime
    
    @property
    def mc(self):
        return self.__minio_client
        
    
    def to_datetime_string(self,date):
        return date.strftime('%m/%d/%Y %I:%M %p')
    
    def to_datetime(self,datestring):
        return datetime.strptime(datestring, '%m/%d/%Y %I:%M %p')
    
    def __generate_assignment_target_file(self):
        if self.__is_assignment:
            late = "LATE-" if not self.__assignment['on_time'] else ""
            filename = f"{late}{self.__netid}.ipynb"
            return f"{self.__instructor_netid}/{self.__lesson}/{self.__filename}/{filename}"
        else:
            return None
    
    def __find_student_netid_on_roster(self):
        return self.__find_in_dataframe(dataframe=self.__roster_df, column_number=0, value=self.__netid)

    def __find_instructor_netid_on_roster(self):
        return self.__find_in_dataframe(dataframe=self.__roster_df, column_number=1, value=self.__netid)
    
    def __find_instructor_by_student(self):
        if self.__is_student:
            student_column = self.__roster_df.columns[0]
            instructor_column = self.__roster_df.columns[1]
            search = self.__roster_df[ self.__roster_df[student_column] ==  self.__netid ]
            row = search.iloc[0].to_list()
            return row[1]
        elif self.__is_instructor:
            return self.__netid
        else:
            return None
    
    
    def __find_in_dataframe(self, dataframe, column_number, value):
        if dataframe.empty : return False
        for val in dataframe.iloc[:,column_number].values:
            if val == value:
                return True
        return False 
        
    def __find_assignment(self):
        result = {}
        if self.__assignments_df.empty: return result
        lesson_column = self.__assignments_df.columns[0]
        assignment_column = self.__assignments_df.columns[1]
        search = self.__assignments_df[ (self.__assignments_df[lesson_column] ==  self.__lesson) & (self.__assignments_df[assignment_column] == self.__filename)]
        if len(search)!=1: return result
        row = search.iloc[0].to_list()
        result['lesson_folder'] = row[0]
        result['filename'] = row[1]
        result['total_points'] = row[2]
        result['gradebook_column'] = row[3]
        result['name'] = row[3].split('|')[0]
        result['duedate'] = row[4]
        result['on_time'] = self.to_datetime(self.__run_datetime)  <=  self.to_datetime(row[4])
        return result 
    
    def __find_filespec(self):
        return f"{os.environ.get('HOME')}/{self.__notebook_path}"
        
    def __find_bucket(self):
        bucket = f"{self.__course}-{self.__git_folder}"
        if self.__minio_client.bucket_exists(bucket):
            return bucket
        else:
            return "empty" # default bucket 
            
    def __find_git_folder(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 3 and items[0] == 'library':
            return self.__settings.get('git-folder',items[2])
        else:
            raise Error('This notebook file is not in a git folder under the course folder.')

    def __find_lesson(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 4 and items[0] == 'library':
            return items[-2]
                
    def __find_filename(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 4 and items[0] == 'library':
            return items[-1]
    
    def __find_course(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 2 and items[0] == 'library':
            return items[1]
        else:
            raise Exception('This notebook file must be in a course folder.')
            
    def __find_service_prefix(self):
        return os.environ.get('JUPYTERHUB_SERVICE_PREFIX')

    def __find_netid(self):
        netid = os.environ.get('JUPYTERHUB_USER')
        decoded_client_id = urllib.parse.unquote(os.environ.get('JUPYTERHUB_CLIENT_ID'))
        if decoded_client_id.find(netid)>=0 and os.environ.get('JUPYTERHUB_SERVICE_PREFIX').find(netid)>=0:
            return netid
        else:
            raise Exception('Unable to locate a netid for this user.')
            
    def __find_notebook_path(self):
        connection_file = os.path.basename(ipykernel.get_connection_file())
        kernel_id = connection_file.split('-', 1)[1].split('.')[0]
        token = os.environ.get("JUPYTERHUB_API_TOKEN")
        netid = self.__netid
        response = requests.get(f'http://127.0.0.1:8888/user/{netid}/api/sessions?token={token}')
        response.raise_for_status()
        sessions = response.json()    
        for sess in sessions:
            if sess['kernel']['id'] == kernel_id:
                return sess['notebook']['path']

