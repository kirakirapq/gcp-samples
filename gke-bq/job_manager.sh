#!/bin/sh
set -e

gcloud config set project ${PROJECT}
gcloud container clusters get-credentials ${CLUSTER} --zone=asia-notheast1-asia

date=`date +%Y%m%d`
echo $date

DIR=./k8s

for file in $DIR/$DEPLOY_ENV*.yaml; do
  if ["`echo $file | grep 'job-manager'`"]; then
    continue
  fi
  sed -i -e "s/yyyymmdd/${date}/g" ${file}
done

kubectl apply -f $DIR/${DEPLOY_ENV}-sample.yaml
kubectl wait --for=condition=complete --timeout=2h --namespace=${NAMESPACE} job/${DEPLOY_ENV}-sample-${date}

echo 'all process finished.'
exit 0
