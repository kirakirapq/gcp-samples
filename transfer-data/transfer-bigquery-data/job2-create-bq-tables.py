# -*- coding: utf-8 -*-
import configparser
import json
from time import sleep
import Log
import os
import subprocess


def makeTables(
        project: str,
        dataset: str,
        table: str,
        schema: str,
        partitioning: bool,
        time_partitioning_field: str = "",
        time_partitioning_expiration: int = 0,
        require_partition_filter: str = "",
        description: str = "") -> dict:

    if partitioning == True:
        if not time_partitioning_field:
            mk = 'bq mk -t --expiration=0 --schema="{schema}"  \
                --time_partitioning_expiration="{time_partitioning_expiration}" \
                --description="{description}" \
                {project}:{dataset}.{table}'.format(
                schema=schema,
                time_partitioning_expiration=time_partitioning_expiration,
                require_partition_filter=require_partition_filter,
                description=description,
                project=project,
                dataset=dataset,
                table=table)
        else:
            mk = 'bq mk -t --expiration=0 --schema="{schema}"  \
                --time_partitioning_field="{time_partitioning_field}" \
                --time_partitioning_expiration="{time_partitioning_expiration}" \
                --require_partition_filter={require_partition_filter} \
                --description="{description}" \
                {project}:{dataset}.{table}'.format(
                schema=schema,
                time_partitioning_field=time_partitioning_field,
                time_partitioning_expiration=time_partitioning_expiration,
                require_partition_filter=require_partition_filter,
                description=description,
                project=project,
                dataset=dataset,
                table=table)
    else:
        mk = 'bq mk -t \
            --expiration=0 \
            --schema="{schema}" \
            --description="{description}" \
            {project}:{dataset}.{table}'.format(
            schema=schema,
            project=project,
            dataset=dataset,
            table=table,
            description=description)
    try:
        check_res = subprocess.getoutput(mk)

        if ("successfully created." in check_res) == True:
            return {"is_success": True, "description": check_res}

        return {"is_success": False, "description": check_res}
    except Exception as e:
        return {"is_success": False, "description": traceback.format_exc()}


if __name__ == '__main__':
    try:
        Log.info('Create Bigquery Tables', "Start Process")

        project = os.environ['PROJECT']
        location = os.environ['DESTINATION_LOCATION']
        env = os.environ['DEPLOY_ENV']

        config_ini = configparser.ConfigParser()
        config_ini.read('./config/config.ini', encoding='utf-8')

        file_name = './config/{}_bq_tables.json'.format(env)
        json_open = open(file_name, 'r')
        json_load = json.load(json_open)

        env_service = '{}-services'.format(env)
        for service in config_ini[env_service]:
            for bq_info in json_load[service]:
                dataset = bq_info['destination_dataset_name']
                tables = bq_info['tables']

                for table_info in tables:
                    table = table_info['name']
                    schema = './bq-schemas/{}/{}'.format(
                        service, table_info['schema'])
                    partitioning = table_info['partitioning']
                    description = table_info['description']
                    if partitioning == True:
                        time_partitioning_field = table_info['time_partitioning_field']
                        time_partitioning_expiration = table_info['time_partitioning_expiration']
                        require_partition_filter = table_info['require_partition_filter']
                    else:
                        time_partitioning_field = ""
                        time_partitioning_expiration = 0
                        require_partition_filter = ""

                    show = 'bq show {project}:{dataset}.{table}'.format(
                        project=project, dataset=dataset, table=table)
                    check_res = subprocess.getoutput(show)

                    if ("Not found" in check_res) == True:
                        count = 0
                        limit = 3
                        while count < limit:
                            response = makeTables(
                                project,
                                dataset,
                                table,
                                schema,
                                partitioning,
                                time_partitioning_field,
                                time_partitioning_expiration,
                                require_partition_filter,
                                description)

                            if response['is_success'] == True:
                                Log.info('Created.', response['description'])
                                break
                            if count == 2:
                                Log.error('Failure Operation.',
                                          response['description'])
                            else:
                                Log.warning('Failure Operation.',
                                            response['description'])
                                sleep(60)

                            count += 1
                    else:
                        Log.info('Skipping Operation.', 'Table {}:{}.{} already exists.'.format(
                            project, dataset, table))

        Log.info('Create Bigquery Tables', "End Process")
    except Exception as e:
        Log.error('Create Bigquery Tables Error', traceback.format_exc())
