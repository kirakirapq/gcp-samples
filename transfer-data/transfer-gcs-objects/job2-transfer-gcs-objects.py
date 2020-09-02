# -*- coding: utf-8 -*-
from time import sleep
import configparser
import json
import Log
import os
import subprocess


def copyObjects(bucket_name: str, destination_bucket_name: str) -> dict:
    copy = "gsutil -m cp gs://{}/\* gs://{}/".format(
        bucket_name, destination_bucket_name)

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

        project = os.environ['PROJECT']
        destination_location = os.environ['DESTINATION_LOCATION']
        env = os.environ['DEPLOY_ENV']

        config_ini = configparser.ConfigParser()
        config_ini.read('./config/config.ini', encoding='utf-8')
        file_name = config_ini[env]['gcs_buckets']

        file_path = './config/{}'.format(file_name)
        json_open = open(file_path, 'r')
        json_load = json.load(json_open)

        env_service = '{}-services'.format(env)
        for bucket_list in config_ini[env_service]:
            for bucket in json_load[bucket_list]:
                bucket_name = bucket['bucket_name']
                destination_bucket_name = bucket['destination_bucket_name']

                count = 0
                limit = 3
                while count < limit:
                    response = copyObjects(
                        bucket_name, destination_bucket_name)

                    if response['is_success'] == True:
                        Log.info('Completed Copy GCS Objects.', 'Success Operation: {}'.format(
                            destination_bucket_name))
                        break
                    if count == 2:
                        Log.error('Failure Operation', response['description'])
                    else:
                        Log.warning('Failure Operation',
                                    response['description'])
                        sleep(60)

                    count += 1
        Log.info('Transfer GCS Object', "End Process")
    except Exception as e:
        Log.error('Transfer GCS Object Error', traceback.format_exc())
