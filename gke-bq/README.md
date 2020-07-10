# GCP - Googl　Kubernetes EngineのJobからBigQueryを利用
## 名前空間作成

```
export CLUSTER=sample-cluster
export NAMESPACE=bq-sample

gcloud container clusters list
gcloud container clusters get-credentials $CLUSTER --zone=asia-northeast1-a
gcloud container clusters list

kubectl get namespaces
kubectl create namespace $NAMESPACE

unset CLUSTER
unset NAMESPACE
```

## シークレット登録
**先にサービスアカウントを作成しておくこと**
BigQuery & Kubernates Engineで必要になるロール

| ロール| 
|:-----------------|
| BigQuery管理者|
| Kubernetes Engine管理者|


```
export SECRET_NAME=bq-sample
export NAMESPACE=bq-sample
export SECRET_FILE=~/Documents/gcp/key/minarai-bq-gke.json

kubectl create secret generic ${SECRET_NAME} --from-file=key.json=${SECRET_FILE} -n ${NAMESPACE}
kubectl get secret -n ${NAMESPACE}

unset SECRET_NAME
unset NAMESPACE
unset SECRET_FILE
```

## GCRへイメージを登録

```
export PROJECT_ID=xxxxxxxxxx
export IMAGE_NAME=bq-sample
export TAG=development
export GCR="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}"

docker build -t ${IMAGE_NAME} .
docker tag ${IMAGE_NAME} ${GCR}
gcloud docker -- push ${GCR}

unset PROJECT_ID
unset IMAGE_NAME
unset TAG
unset GCR
```

## Job実行

```
kubectl apply -f ./k8s/dev-sample.yaml
```
