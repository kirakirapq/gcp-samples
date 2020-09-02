# -*- coding: utf-8 -*-
from time import sleep
import configparser
import json
import Log
import os
import subprocess


def createBucket(project: str, location: str, bucket_name: str) -> dict:
    """バケットを作成
        https://cloud.google.com/storage/docs/gsutil/commands/mb?hl=ja

    Args:
        project (str): [description]
        location (str): [description]
        bucket_name (str): [description]

    Returns:
        dict: [description]
    """
    mb = 'gsutil mb -p {project} -c STANDARD -l {location} -b on gs://{bucket_name}/'.format(
        project=project,
        location=location,
        bucket_name=bucket_name)
    try:
        check_res = subprocess.getoutput(mb)

        if ("Creating" in check_res) == True:
            return {"is_success": True, "description": check_res}

        return {"is_success": False, "description": check_res}
    except Exception as e:
        return {"is_success": False, "description": traceback.format_exc()}


def attachMember(member_type: str, member_name: str, iam_role: str, bucket_name: str) -> dict:
    """バケットへmemberをアタッチ
        https://cloud.google.com/storage/docs/gsutil/commands/iam?hl=ja

    Args:
        member_type (str): [description]
        member_name (str): [description]
        iam_role (str): [description]
        bucket_name (str): [description]

    Returns:
        dict: [description]
    """
    attach = 'gsutil iam ch {member_type}:{member_name}:{iam_role} gs://{bucket_name}'.format(
        member_type=member_type,
        member_name=member_name,
        iam_role=iam_role,
        bucket_name=bucket_name)

    try:
        check_res = subprocess.getoutput(attach)

        if len(check_res) == 0 or ("No changes" in check_res) == True:
            return {"is_success": True, "description": check_res}

        return {"is_success": False, "description": check_res}
    except Exception as e:
        return {"is_success": False, "description": traceback.format_exc()}


if __name__ == '__main__':
    try:
        Log.info('Create GCS bucket', "Start Process")

        project = os.environ['PROJECT']
        location = os.environ['DESTINATION_LOCATION']
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

                member_type = bucket['attach_member']['member_type']
                member_name = bucket['attach_member']['member_name']
                iam_role = bucket['attach_member']['iam_role']

                try:
                    Log.info('Create GCS bucket', 'bucket_name: {}'.format(
                        destination_bucket_name))
                    ls = 'gsutil ls gs://{}'.format(destination_bucket_name)
                    check_res = subprocess.getoutput(ls)

                    if ("40" in check_res) == True or "gs://{}".format(destination_bucket_name) in check_res == False:
                        count = 0
                        limit = 3
                        while count < limit:
                            response = createBucket(
                                project, location, destination_bucket_name)
                            if response['is_success'] == True:
                                Log.info('Create GCS bucket', 'Success Operation: {}'.format(
                                    destination_bucket_name))
                                break
                            if count == 2:
                                Log.error('Create GCS bucket',
                                          response['description'])
                            else:
                                Log.warning('Create GCS bucket',
                                            response['description'])
                                sleep(60)

                            count += 1
                    else:
                        Log.info(
                            'Skipping Create GCS bucket Job', 'This Bucket already exists.: {}'.format(destination_bucket_name))

                    Log.info('Attach Member', 'bucket_name: {}'.format(
                        destination_bucket_name))
                    ls = 'gsutil ls gs://{}'.format(destination_bucket_name)
                    check_res = subprocess.getoutput(ls)

                    member_op_count = 0
                    member_op_limit = 3
                    while member_op_count < member_op_limit:
                        response = attachMember(
                            member_type, member_name, iam_role, destination_bucket_name)
                        if response['is_success'] == True:
                            Log.info('Attach Member', 'Success Operation: {}'.format(
                                destination_bucket_name))
                            break
                        if member_op_count == 2:
                            Log.error('Attach Member', response['description'])
                        else:
                            Log.warning('Attach Member',
                                        response['description'])
                            sleep(60)

                        member_op_count += 1

                except Exception as e:
                    Log.error('Failure Operation', traceback.format_exc())
        Log.info('Create GCS bucket', "End Process")
    except Exception as e:
        Log.error('Create GCS bucket Error', traceback.format_exc())
