# -*- coding: utf-8 -*-
import configparser
import json
from time import sleep
import Log
import os
import subprocess


def exportBigQueryTableData(location: str, project: str, dataset: str, table: str, bucket: str) -> dict:

    export = 'bq --location={location} extract \
                --destination_format CSV \
                --compression GZIP \
                --print_header=true \
                {project}:{dataset}.{table} \
                gs://{bucket}/{dataset}/{table}/*.csv.gz'.format(
        location=location,
        project=project,
        dataset=dataset,
        table=table,
        bucket=bucket)

    try:
        check_res = subprocess.getoutput(export)

        if ("DONE" in check_res) == True:
            return {"is_success": True, "description": check_res}

        return {"is_success": False, "description": check_res}
    except Exception as e:
        return {"is_success": False, "description": traceback.format_exc()}


if __name__ == '__main__':
    try:
        Log.info('Export Bigquery Table Data Job', "Start Process")

        project = os.environ['PROJECT']
        destination_location = os.environ['DESTINATION_LOCATION']
        env = os.environ['DEPLOY_ENV']
        source_location = os.environ['SOURCE_LOCATION']

        config_ini = configparser.ConfigParser()
        config_ini.read('./config/config.ini', encoding='utf-8')

        env_bucket = '{}-export-bucket'.format(env)
        bucket = config_ini[env_bucket]['bucket_name']

        file_name = './config/{}_bq_tables.json'.format(env)
        json_open = open(file_name, 'r')
        json_load = json.load(json_open)

        env_service = '{}-services'.format(env)
        for service in config_ini[env_service]:
            for bq_info in json_load[service]:
                dataset = bq_info['dataset_name']
                tables = bq_info['tables']

                for table_info in tables:
                    table = table_info['name']

                    count = 0
                    limit = 3
                    while count < limit:
                        response = exportBigQueryTableData(
                            source_location, project, dataset, table, bucket)

                        if response['is_success'] == True:
                            Log.info('Exported.', response['description'])
                            break
                        if count == 2:
                            Log.error('Failure Operation.',
                                      response['description'])
                        else:
                            Log.warning('Failure Operation.',
                                        response['description'])
                            sleep(60)

                        count += 1

        Log.info('Export Bigquery Table Data Job', "End Process")
    except Exception as e:
        Log.error('Export Bigquery Table Data Job Error',
                  traceback.format_exc())
