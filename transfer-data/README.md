# リージョン移行手順

### 1. 環境変数をセット
* development operation
```
export DEPLOY_ENV=dev
export PROJECT=gree-ua-kpi-dev
export DESTINATION_LOCATION=us-east1
export SOURCE_LOCATION=asia-northeast1
```

* qa operation
```
export DEPLOY_ENV=qa
export PROJECT=gree-ua-kpi-dev
export DESTINATION_LOCATION=us-east1
export SOURCE_LOCATION=asia-northeast1
```

* production operation
```
export DEPLOY_ENV=prd
export PROJECT=gree-ua-kpi
export DESTINATION_LOCATION=us-east1
export SOURCE_LOCATION=asia-northeast1
```

### 2. 設定ファイルを更新

#### 2-1. Cloud Storageの移行設定

* 2-1-1. `transfer-gcs-objects/config/config.ini` の設定
　バケットは`${DEPLOY_ENV}`に作成できます。
  バケットの詳細設定はJSONで記述するので、ここでは記述されたJSONファイルのファイル名を設定します。
  変更しない場合は `dev_gsc_buckets.json`, `qa_gsc_buckets.json`, `prd_gsc_buckets.json`のファイルが設定されています。

* 2-1-2. `transfer-gcs-objects/config/${DEPLOY_ENV}_gsc_buckets.json` の設定
　1階層のキーはサービス名を入れてください。  
　変更する場合は下記 `2-1-3`と`2-1-4`に従ってコードも書き換えてください。  
　システムで利用している`attach_member`はサービスアカウントを設定します。

* 2-1-3. `transfer-gcs-objects/job1-create-gcs-buckets.py` の設定
`TODO`としているのですが、Line 84 `bucket_list`は`${DEPLOY_ENV}_gsc_buckets.json`で入力した1階層目のkeyを設定します。

* 2-1-4. `transfer-gcs-objects/job2-transfer-gcs-objects.py` の設定
`TODO`としているのですが、Line 42 `bucket_list`は`${DEPLOY_ENV}_gsc_buckets.json`で入力した1階層目のkeyを設定します。


#### 2-2. BigQueryの移行設定



### 3. データ転送先のCloud Storageバケットを用意する
* バケット名: `./transfer-bigquery-data/config/config.ini`の`${DEPLOY_ENV}-export-bucket`を参照
* 作成コマンド
```
gsutil mb -p ${PROJECT} -c STANDARD -l {DESTINATION_LOCATION} -b on gs://{bucket_name}/
```


### 4. ジョブの実行
#### 4-1. Cloud Storageデータの転送
* Cloud Storageデータの転送ディレクトリへ移動
```
cd transfer-gcs-objects
```

* 4-1-1. 転送先バケットを作成
```
% python3 job1-create-gcs-buckets.py
```

* 4-1-2. バケット内のオブジェクトをコピー（転送）
```
% python3 job2-transfer-gcs-objects.py
```


#### 4-2. BigQueryデータの転送
* BigQueryデータの転送ジョブディレクトリへ移動
```
cd transfer-bigquery-data
```

* 4-2-1. 転送先データセットの作成
```
% python3 job1-create-bq-datasets.py
```

* 4-2-2. 転送先テーブルの作成
```
% python3 job2-create-bq-tables.py
```

* 4-2-3. 転送元データをCloud Storageへエクスポート
```
% python3 job3-export-bq-table-data.py
```

* 4-2-4. Cloud Storageのデータを転送
```
python3 job4-transfer-gsc-objects.py
```

* 4-2-5. 転送先テーブルへデータをインポート
```
% python3 job5-import-bq-table-data.py
```
