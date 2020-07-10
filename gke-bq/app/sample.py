from google.cloud import bigquery

# インスタンス生成
client = bigquery.Client()


query = """
    SELECT name, sex
    FROM `samples.sample_animal`
    LIMIT 100
"""
# API リクエスト
query_job = client.query(query)

# 取得データへアクセス
for row in query_job:
    # Row values can be accessed by field name or index.
    print("名前={}, 性別={}".format(row["name"], row["sex"]))
