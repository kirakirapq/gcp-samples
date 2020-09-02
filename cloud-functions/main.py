# coding: utf-8
from google.cloud import bigquery


def load_bigquery(data, context):
    """Background Cloud Function to be triggered by Cloud Storage.
         Load To Bigquery

      Args:
          data (dict): The Cloud Functions event payload.
          context (google.cloud.functions.Context): Metadata of triggering event.
      Returns:
          None; the output is written to Stackdriver Logging
      """
    print('Event ID: {}'.format(context.event_id))
    print('Event type: {}'.format(context.event_type))
    print('Bucket: {}'.format(data['bucket']))
    print('File: {}'.format(data['name']))
    print('Metageneration: {}'.format(data['metageneration']))
    print('Created: {}'.format(data['timeCreated']))
    print('Updated: {}'.format(data['updated']))

    client = bigquery.Client()

    # データセットをセット
    dataset_id = 'samples'
    dataset_ref = client.dataset(dataset_id)
    table_name = 'test'

    job_config = bigquery.LoadJobConfig()
    # スキーマ定義
    job_config.schema = [
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("age", "INTEGER"),
    ]
    # 開始行はスキップ
    job_config.skip_leading_rows = 1
    # フォーマットを指定
    job_config.source_format = bigquery.SourceFormat.CSV
    # GSCのリソースURI
    uri = "gs://{}/{}".format(data['bucket'], data['name'])
    # API リクエスト
    load_job = client.load_table_from_uri(
        uri, dataset_ref.table(table_name), job_config=job_config
    )
    print("Starting job {}".format(load_job.job_id))
    # 結果を表示
    load_job.result()  # Waits for table load to complete.
    print("Job finished.")

    # テーブルからデータを取得　GCSからのデータ取り込み確認
    destination_table = client.get_table(dataset_ref.table(table_name))
    print("Loaded {} rows.".format(destination_table.num_rows))
