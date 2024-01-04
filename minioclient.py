from minio import Minio
import os

#You can explore the Console using https://play.min.io:9443. Log in with the following credentials:
#Username: Q3AM3UQ867SPQQA43P2F
#Password: zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
# 'host': os.environ.get("S3_HOST",'minio.cent-su.org:9000'),
# 'key': os.environ.get("S3_KEY",'sesuro5pka32vtt'),
# 'secret': os.environ.get("S3_SECRET",'c5977GQW2CHF6wsNG5bK'),


class MinioClient(object):

    def __init__(self):
        self.__minio_credentials = {
            'host': os.environ.get("S3_HOST", 'play.min.io:9000'),
            'key': os.environ.get("S3_KEY", 'Q3AM3UQ867SPQQA43P2F'),
            'secret': os.environ.get("S3_SECRET", 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'),
            'secure': os.environ.get("S3_SECURE", "true").lower() == "true"
            }
        self.__mc = Minio(self.__minio_credentials['host'],
                          access_key=self.__minio_credentials['key'],
                          secret_key=self.__minio_credentials['secret'],
                          secure=self.__minio_credentials['secure'])

        #print(minio_credentials)

    @property
    def credentials(self):
        return self.__minio_credentials

    @property
    def alias_url(self):
        proto = "https://" if self.__minio_credentials['secure'] else "http://"
        return f"{proto}{self.__minio_credentials['host']} {self.__minio_credentials['key']} {self.__minio_credentials['secret']}"

        #https://play.min.io:9000 Q3AM3UQ867SPQQA43P2F zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG


    def bucket_exists(self, bucket_name):
        return self.__mc.bucket_exists(bucket_name)

    def make_bucket(self,bucket_name):
        if not self.bucket_exists(bucket_name):
            self.__mc.make_bucket(bucket_name)
        return self.bucket_exists(bucket_name)

    def get_info(self, bucket_name, remote_filespec):
        items = self.__mc.list_objects(bucket_name,prefix=remote_filespec)
        for item in items:
            if item.object_name==remote_filespec:
                return item
        return None    
    def put(self, bucket_name, local_filespec, remote_filespec):
        with open (local_filespec, 'rb') as f:
            stats = os.stat(local_filespec)
            etag = self.__mc.put_object(bucket_name, remote_filespec, f , stats.st_size )
            return etag

    def get(self, bucket_name, remote_filespec):
        return self.__mc.get_object(bucket_name, remote_filespec)        

    def fput(self,bucket_name,local_filespec, remote_filespec):
        result = self.__mc.fput_object(bucket_name, remote_filespec, local_filespec)
        return result

    def fget(self,bucket_name,remote_filespec, local_filespec):
        info = self.__mc.fget_object(bucket_name, remote_filespec, local_filespec)
        return info

if __name__=='__main__':
    pass