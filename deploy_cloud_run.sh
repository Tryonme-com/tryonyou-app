#!/bin/bash
set -e
export PROJECT_ID="gen-lang-client-0091228222"
export REGION="europe-west1"
export SERVICE_NAME="tryonyou-app"
export IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:v100-omega"

echo "================================================================================"
echo "EJECUTANDO GOOGLE CLOUD BUILD Y CLOUD RUN"
echo "================================================================================"

gcloud config set project ${PROJECT_ID}
gcloud builds submit --tag ${IMAGE_NAME} .

gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_NAME} \
    --region=${REGION} \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="DEPLOYMENT_ID=V9-LAFAYETTE-2026-LIVE,SIREN_ISSUER=943610196,BANK_DESTINATION=Hello Balín" \
    --min-instances=1 \
    --max-instances=10 \
    --quiet
