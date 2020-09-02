# リージョン移行手順

## 1. 環境変数をセット
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

## 2. 設定ファイルを更新

### 2-1. Cloud Storageの移行設定

#### 2-1-1. `transfer-gcs-objects/config/config.ini` の設定  
  バケットは`${DEPLOY_ENV}`に作成できます。  
  バケットの詳細設定はJSONで記述するので、ここでは記述されたJSONファイルのファイル名を設定します。  
  変更しない場合は `dev_gsc_buckets.json`, `qa_gsc_buckets.json`, `prd_gsc_buckets.json`のファイルが設定されています。  
  サービス名は`2ー1ー2` GCSバケットの詳細設定時に登録するサービス名と整合性がとれている必要があります

|  項目  |  内容  |
| ---- | ---- |
|  ${DEPLOY_ENV}  |  環境名  |
|  ${DEPLOY_ENV}　gcs_buckets  |  バケットの設定を記述するファイル名をセット  |
|  ${DEPLOY_ENV}-services |  サービス名（任意）を登録  |

* 設定例
```
[dev]
gcs_buckets=dev_gcs_buckets.json

; 命名規則：${DEPLOY_ENV}-services
; dev_gcs_backets.jsonで登録した利用するサービスをセット
[dev-services]
sample-service1=
```

#### 2-1-2. `transfer-gcs-objects/config/${DEPLOY_ENV}_gsc_buckets.json` の設定  
　1階層のキーはサービス名を入れてください。   
　システムで利用している`attach_member`はサービスアカウントを設定します。

|  項目  |  内容  |
| ---- | ---- |
|  bucket_name  |  移行元バケット名  |
|  destination_bucket_name  |  移行先バケット名  |
|  attach_member  |  権限を追加するメンバーを登録  |
|  attach_member.member_type |  serviceAccount  |
|  attach_member.member_name |  アカウント名  |
|  attach_member.iam_role |  IAMロール  |

* 設定例
```
{
	"sample-service1": [
		{
			"bucket_name": "sample-asia-northeast1-bucket",
			"destination_bucket_name": "sample-us-east1-bucket",
			"attach_member": {
				"member_type": "serviceAccount",
				"member_name": "サービスアカウント名@プロジェクトID.iam.gserviceaccount.com",
				"iam_role": "roles/storage.admin"
			}
		}
	]
}
```


### 2-2. BigQueryの移行設定
#### 2-2-1. `transfer-bigquery-data/config/config.ini` の設定  
　Datasetは`${DEPLOY_ENV}`ごとに作成できます。  
　`config.ini`への記述項目  
　1. 移行先のデータセットを`${DEPLOY_ENV}-datasets`を設定  
　2. `${DEPLOY_ENV}-export-bucket`に`bucket_name=エクスポートバケット名`,`destination_bucket_name=インポートバケット名`を設定  
　3. `${DEPLOY_ENV}-services`へサービスを設定　サービス名は移行を行うサービスの名称で任意の名前つけられます。

|  項目  |  内容  |
| ---- | ---- |
|  ${DEPLOY_ENV}-datasets  |  作成するデータセットの一覧を記載  |
|  ${DEPLOY_ENV}-export-bucket  |  移行する際に使うバケットの設定  |
|  ${DEPLOY_ENV}-export-bucket　bucket_name  |  移行データのエクスポート先バケット名  |
|  ${DEPLOY_ENV}-export-bucket　destination_bucket_name |  移行データのインポート先バケット名  |
|  ${DEPLOY_ENV}-services |  サービス名（任意）を登録  |

※ 設定例
下記設定例の場合、`DESTINATION_LOCATION`でセットしたロケーションに`sample_dataset_us_east1`, `my_game`のデータセットを作成する
任意のサービスをつけて移行の管理を行う  
サービス名は`2ー2ー2` データセットの詳細設定時に登録するサービス名と整合性がとれている必要があります

```
[dev-datasets]
sample_dataset_us_east1=

[dev-export-bucket]
bucket_name=export-bq-data
destination_bucket_name=import-bq-data

[dev-services]
sample=
```

#### 2-2-2. `transfer-bigquery-data/config/${DEPLOY_ENV}_bq_tables.json` の設定  
　1階層のキーはサービス名を入れてください。  

|  項目  |  内容  |
| ---- | ---- |
|  dataset_name  |  移行元データセット名  |
|  destination_dataset_name  |  移行先データセット名  |
|  tables  |  移行するテーブル情報  |
|  tables.name |  移行するテーブル名  |
|  tables.schema |  テーブルスキーマ名  |
|  tables.partitioning |  パーテション有無  |
|  tables.time_partitioning_field |  パーテションフィールド  |
|  tables.time_partitioning_field |  パーテションフィールド  |
|  tables.time_partitioning_expiration |  パーテション期限 |
|  tables.require_partition_filter |  パーテションフィルタ必須可否 |
|  tables.description |  description |

* 設定例

```
{
	"sample": [
		{
			"dataset_name": "sample_dataset_asia_northast1",
			"destination_dataset_name": "sample_dataset_us_east1",
			"tables": [
				{
					"name": "sample_table1",
					"schema": "sample_table1.json",
					"partitioning": true,
					"time_partitioning_field": "date",
					"time_partitioning_expiration": 0,
					"require_partition_filter": false,
					"description": ""
				},
				{
					"name": "sample_table2",
					"schema": "sample_table2.json",
					"partitioning": true,
					"time_partitioning_field": "date",
					"time_partitioning_expiration": 0,
					"require_partition_filter": true,
					"description": ""
				}
			]
		}
	]
}
```


## 3. データ転送先のCloud Storageバケットを用意する
* バケット名: `./transfer-bigquery-data/config/config.ini`の`${DEPLOY_ENV}-export-bucket`を参照
* 作成コマンド
```
gsutil mb -p ${PROJECT} -c STANDARD -l {DESTINATION_LOCATION} -b on gs://{bucket_name}/
```


## 4. ジョブの実行
### 4-1. Cloud Storageデータの転送
* Cloud Storageデータの転送ディレクトリへ移動
```
cd transfer-gcs-objects
```

#### 4-1-1. 転送先バケットを作成
```
% python3 job1-create-gcs-buckets.py
```

####  4-1-2. バケット内のオブジェクトをコピー（転送）
```
% python3 job2-transfer-gcs-objects.py
```


### 4-2. BigQueryデータの転送
* BigQueryデータの転送ジョブディレクトリへ移動
```
cd transfer-bigquery-data
```

#### 4-2-1. 転送先データセットの作成
```
% python3 job1-create-bq-datasets.py
```

#### 4-2-2. 転送先テーブルの作成
```
% python3 job2-create-bq-tables.py
```

#### 4-2-3. 転送元データをCloud Storageへエクスポート
```
% python3 job3-export-bq-table-data.py
```

#### 4-2-4. Cloud Storageのデータを転送
```
python3 job4-transfer-gsc-objects.py
```

#### 4-2-5. 転送先テーブルへデータをインポート
```
% python3 job5-import-bq-table-data.py
```
