from .nbenvironment import NbEnvironment
from dateutil import tz
from datetime import datetime
from minio.error import S3Error

class Submission:
    
    def __init__(self):
        try:
            self.env = NbEnvironment()
        except S3Error as e:
            print("ERROR: Likely cause: File is not in a course folder.")
            raise e
        except Exception as e:
            print(e)
            raise e
            
    @property
    def properties(self):
        return self.env.properties
    
    
    def submit(self):
        '''
        Perform a Submission
        '''
        if not self.env.is_assignment:
            raise Exception(f"ERROR: Thie file {self.env.filename} is not on the assignment list. Please check the assignment you are supposed to submit.")
            
        if not self.env.is_student:
            raise Exception(f"ERROR: Your netid {self.env.netid} does not appear on the {self.env.course} roster.")
            
        print("=== SUBMISSON DETAILS ===")
        print(f"Your Netid ............. {self.env.netid}")
        print(f"Your Instructor ........ {self.env.instructor_netid}")        
        print(f"Assigment Name ......... {self.env.filename}")
        print(f"Submission Date ........ {self.env.run_datetime}")
        print(f"Assignment Due Date .... {self.env.assignment['duedate']}")
        
        if not self.env.assignment['on_time']:            
            print("\n=== WARNING: Your Submission is LATE! ===")
            print(f"Your Submission Date   : {self.env.run_datetime}")
            print(f"Due Date For Assignment: {self.env.assignment['duedate']}")
            late_confirm = input("Submit This Assignment Anyways [y/n] ?").lower()
            if late_confirm == 'n':
                print("Aborting Submission.")
                return
        target_file = self.env.mc.get_info(self.env.bucket, self.env.assignment_target_file)
        if target_file != None:
                last_mod = target_file.last_modified.astimezone(tz.gettz(self.env.timezone))
                print("\n=== WARNING: This is a Duplicate Submission ==")
                print(f"You Submitted This Assigment On: {self.env.to_datetime_string(last_mod)}")
                again = input("Overwrite Your Previous Submission [y/n] ? ").lower()
                if again == 'n':
                    print("Aborting.")
                    return
                
        print("\n=== SUBMITTING  ===")
        print(f"Uploading: {self.env.filename}\nTo: {self.env.assignment_target_file} ...")
        result = self.env.mc.fput(self.env.bucket,self.env.filespec,self.env.assignment_target_file)
        print(f"Done!\nReciept: {result.etag}")
        
        
        
