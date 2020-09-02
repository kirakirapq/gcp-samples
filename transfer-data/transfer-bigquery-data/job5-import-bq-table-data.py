# -*- coding: utf-8 -*-
import configparser
import json
from time import sleep
import Log
import os
import subprocess


def importToBigQueryTableData(
        location: str,
        project: str,
        dataset: str,
        table: str,
        path_to_source: str,
        schema: str) -> dict:

    import_data = 'bq --location={location} load \
              --skip_leading_rows=1 \
              --source_format=CSV \
              {project}:{dataset}.{table} \
              {path_to_source} \
              {schema}'.format(
        location=location,
        project=project,
        dataset=dataset,
        table=table,
        path_to_source=path_to_source,
        schema=schema)
    try:
        msg = "sorce: {}, table: {}:{}.{}, schema: {}".format(
            path_to_source, project, dataset, table, schema)
        Log.info("Load Start", msg)

        check_res = subprocess.getoutput(import_data)

        if ("DONE" in check_res) == True:
            return {"is_success": True, "description": check_res}

        return {"is_success": False, "description": check_res}
    except Exception as e:
        return {"is_success": False, "description": traceback.format_exc()}


if __name__ == '__main__':
    try:
        Log.info('Import Bigquery Table Data Job', "Start Process")

        project = os.environ['PROJECT']
        destination_location = os.environ['DESTINATION_LOCATION']
        env = os.environ['DEPLOY_ENV']
        source_location = os.environ['SOURCE_LOCATION']

        config_ini = configparser.ConfigParser()
        config_ini.read('./config/config.ini', encoding='utf-8')

        env_bucket = '{}-export-bucket'.format(env)
        destination_bucket = config_ini[env_bucket]['destination_bucket_name']

        file_name = './config/{}_bq_tables.json'.format(env)
        json_open = open(file_name, 'r')
        json_load = json.load(json_open)

        env_service = '{}-services'.format(env)
        for service in config_ini[env_service]:
            for bq_info in json_load[service]:
                sorce_dataset = bq_info['dataset_name']
                destination_dataset = bq_info['destination_dataset_name']
                tables = bq_info['tables']

                for table_info in tables:
                    table = table_info['name']
                    schema = './bq-schemas/{}/{}'.format(
                        service, table_info['schema'])

                    path_to_source = 'gs://{bucket}/{dataset}/{table}/*'.format(
                        bucket=destination_bucket,
                        dataset=sorce_dataset,
                        table=table)
                    count = 0
                    limit = 3
                    while count < limit:
                        response = importToBigQueryTableData(
                            destination_location, project, destination_dataset, table, path_to_source, schema)

                        if response['is_success'] == True:
                            Log.info('Imported.', response['description'])
                            break
                        if count == 2:
                            Log.error('Failure Operation.',
                                      response['description'])
                        else:
                            Log.warning('Failure Operation.',
                                        response['description'])
                            sleep(60)

                        count += 1

        Log.info('Import Bigquery Table Data Job', "End Process")
    except Exception as e:
        Log.error('Import Bigquery Table Data Job Error',
                  traceback.format_exc())
