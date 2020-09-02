# -*- coding: utf-8 -*-
from time import sleep
import configparser
import Log
import os
import subprocess

def copyObjects(source_bucket: str, destination_bucket: str) -> dict:
    copy = "gsutil -m cp -r gs://{}/\* gs://{}/".format(source_bucket, destination_bucket)

    try:
        check_res = subprocess.getoutput(copy)

        if ("completed" in check_res) == True:
            return {"is_success": True, "description": check_res}

        return {"is_success": False, "description": check_res}
    except Exception as e:
        return {"is_success": False, "description": traceback.format_exc()}

if __name__ == '__main__':
    try:
        Log.info('Transfer GCS Object', "Start Process")

        project              = os.environ['PROJECT']
        destination_location = os.environ['DESTINATION_LOCATION']
        env                  = os.environ['DEPLOY_ENV']

        config_ini = configparser.ConfigParser()
        config_ini.read('./config/config.ini', encoding='utf-8')

        env_bucket         = '{}-export-bucket'.format(env)
        source_bucket_name      = config_ini[env_bucket]['bucket_name']
        destination_bucket_name = config_ini[env_bucket]['destination_bucket_name']

        bucket_name = config_ini[env_bucket]['bucket_name']
        bucket_name = config_ini[env_bucket]['destination_bucket_name']

        count = 0
        limit = 3
        while count < limit:
            response = copyObjects(source_bucket_name, destination_bucket_name)

            if response['is_success'] == True:
                Log.info('Completed Copy GCS Objects.', 'Success Operation: {}'.format(destination_bucket_name))
                break
            if count == 2:
                Log.error('Failure Operation', response['description'])
            else:
                Log.warning('Failure Operation', response['description'])
                sleep(60)

            count += 1

        Log.info('Transfer GCS Object Job', "End Process")
    except Exception as e:
         Log.error('Transfer GCS Object Job Error', traceback.format_exc())
