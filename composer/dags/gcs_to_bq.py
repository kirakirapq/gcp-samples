import os
import logging
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 5, 19),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'gcs_to_bigquery',
    default_args=default_args,
    schedule_interval=timedelta(days=1))
dag.doc_md = __doc__

# DAG 始点と終点の宣言
start_task = DummyOperator(task_id="start", dag=dag)
end_task = DummyOperator(task_id="end", dag=dag)


class TableConfig:
    """
    Holds config for the export/import job we are creating.
    """
    STANDARD_EXPORT_QUERY = None
    _STANDARD_EXPORT_QUERY = "SELECT * from {}"

    def __init__(
            self,
            import_dataset: str,
            import_table: str,
            partition_decorator: str,
            export_bucket: str,
            export_file: str,
            bq_schema_bucket: str,
            gcp_project: str,
            bq_location: str):
        """
        Arguments:
            import_dataset {str} -- [description]
            import_table {str} -- [description]
            partition_decorator {str} -- [description]
            export_bucket {str} -- [description]
            export_file {str} -- [description]
            bq_schema_bucket {str} -- [description]
            gcp_project {str} -- [description]
            bq_location {str} -- [description]
        """
        self.params = {
            'import_dataset': import_dataset,
            'import_table': import_table,
            'partition_decorator': partition_decorator,
            'export_bucket': export_bucket,
            'export_file': export_file,
            'bq_schema_bucket': bq_schema_bucket,
            'gcp_project': gcp_project,
            'bq_location': bq_location
        }


def get_table_config(import_dataset: str, import_table: str, partition_decorator: str, export_bucket: str, export_file: str, bq_schema_bucket: str):
    """TableConfig生成ファクトリーメソッド
    Arguments:
      import_dataset {str}
      import_table {str}
      partition_decorator {str}
      export_bucket {str}
      export_file {str}
      bq_schema_bucket {str}
    Returns:
      TableConfig
    """
    return TableConfig(
        import_dataset=import_dataset,
        import_table=import_table,
        partition_decorator=partition_decorator,
        export_bucket=export_bucket,
        export_file=export_file,
        bq_schema_bucket=bq_schema_bucket,
        gcp_project=os.environ.get('PROJECT_ID'),
        bq_location=os.environ.get('BQ_LOCATION'))


def get_import_table_task(table_config):
    """GSCからBigQueryへデータをインポートする
    Arguments:
      table_config {TableConfig}
    Returns:
      BashOperator
    """
    import_task = BashOperator(
        task_id='from_{}_import_bigquery'.format(
            table_config.params['export_bucket']),
        params=table_config.params,
        bash_command="""
      gsutil cp gs://{{ params.bq_schema_bucket }}/{{ params.import_table }}.json {{ params.import_table }}.json
      cat {{ params.import_table }}.json

      bq --project_id {{ params.gcp_project }} --location={{ params.bq_location }} load --skip_leading_rows=1 --replace  \
      --source_format=CSV {{ params.import_dataset }}.{{ params.import_table }}\${{ params.partition_decorator }} \
      gs://{{ params.export_bucket }}/{{ params.export_file }} {{ params.import_table }}.json
      """,
        dag=dag)

    import_task.doc_md = """#### Import table from storage to bigquery　task documentation"""

    return import_task


target_date = datetime.today().strftime('%Y%m%d')

table_config = get_table_config(
    import_dataset="exsample_composer_dataset",
    import_table="exsample_composer_table",
    partition_decorator=target_date,
    export_bucket="exsample-composer-gcs",
    export_file="exsample_composer_table_*.csv",
    bq_schema_bucket="exsample-composer-schemas")
from_gcs_import_bq_task = get_import_table_task(table_config)


start_task >> from_gcs_import_bq_task >> end_task
