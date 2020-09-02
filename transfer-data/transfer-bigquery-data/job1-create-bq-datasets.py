# -*- coding: utf-8 -*-
from time import sleep
import configparser
import Log
import os
import subprocess

def makeDatasets(project: str, location: str, dataset: str, integer1: int = 0) -> dict:
    mb = 'bq --location={location} mk \
            --dataset \
            --default_table_expiration {integer1} \
            {project}:{dataset}'.format(
                project = project,
                dataset = dataset,
                location = location,
                integer1 = integer1)
    try:
        check_res = subprocess.getoutput(mb)

        if ("successfully created." in check_res) == True:
            return {"is_success": True, "description": check_res}

        return {"is_success": False, "description": check_res}
    except Exception as e:
        return {"is_success": False, "description": traceback.format_exc()}

if __name__ == '__main__':
    try:
        Log.info('Create Bigquery Datasets', "Start Process")

        project   = os.environ['PROJECT']
        location  = os.environ['DESTINATION_LOCATION']
        env       = '{}-datasets'.format(os.environ['DEPLOY_ENV'])

        config_ini = configparser.ConfigParser()
        config_ini.read('./config/config.ini', encoding='utf-8')
        datasets = config_ini[env]

        for dataset in datasets:
            show = 'bq show {project}:{dataset}'.format(project = project, dataset = dataset)
            check_res = subprocess.getoutput(show)

            if ("Not found" in check_res) == True:
                count = 0
                limit = 3
                while count < limit:
                    response = makeDatasets(project, location, dataset)
                    if response['is_success'] == True:
                        Log.info('Created.', response['description'])
                        break
                    if count == 2:
                        Log.error('Failure Operation.', response['description'])
                    else:
                        Log.warning('Failure Operation.', response['description'])
                        sleep(60)

                    count += 1
            else:
                Log.info('Skipping Operation.', 'Dataset {}:{} already exists.'.format(project, dataset))

        Log.info('Create Bigquery Datasets', "End Process")
    except Exception as e:
         Log.error('Create Bigquery Datasets Error', traceback.format_exc())
