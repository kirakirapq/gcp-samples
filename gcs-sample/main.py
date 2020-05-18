import logging
import os

from flask import Flask, request, jsonify
from google.cloud import storage

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

ALLOWED_EXTENSIONS = {'csv'}

def get_file(file_name):
  """GSCからデータを読み込む

  Arguments:
      fname {string} -- 対象のファイル名を指定
  """
  bucket_name = os.environ.get('BUCKET_NAME')
  project_name = os.environ.get('PROJECT_ID')

  #プロジェクト名を指定してclientを作成
  gcs = storage.Client(project_name)
  #バケット名を指定してbucketを取得
  bucket = gcs.get_bucket(bucket_name)
  #Blobを作成
  blob = storage.Blob(file_name, bucket)
  content = blob.download_as_string()
 
  return content

@app.route('/gcs-api/file',  methods=['GET'])
def index():
  file_name = request.args.get('file_name', default='', type=str)
  data = get_file(file_name)
  
  return data
  return jsonify({
    "result": data
  })

@app.route('/gcs-api/file/<string:file_name>', methods=['GET'])
def get_data(file_name=''):
    data = get_file(file_name)
  
    return data

@app.route('/gcs-api/upload',  methods=['POST'])
def upload():
  uploaded_file = request.files.get('file')

  if not uploaded_file:
        return 'No file uploaded.', 400
  bucket_name = os.environ.get('BUCKET_NAME')
  project_name = os.environ.get('PROJECT_ID')

  file_name = uploaded_file.filename
  content   = uploaded_file.read()

  logging.debug(file_name)
  
  # Create a Cloud Storage client.
  gcs = storage.Client(project_name)

  # Get the bucket that the file will be uploaded to.
  bucket = gcs.get_bucket(bucket_name)

  # Create a new blob and upload the file's content.
  blob = bucket.blob(file_name)

  blob.upload_from_string(
        content,
        content_type=uploaded_file.content_type
    )

  return blob.public_url

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == '__main__':
  app.run()