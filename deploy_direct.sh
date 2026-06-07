#!/bin/bash
set -e
export PROJECT_ID="gen-lang-client-0091228222"
export REGION="europe-west1"
export SERVICE_NAME="tryonyou-app"

echo "================================================================================"
echo "DESPLIEGUE DIRECTO A GOOGLE CLOUD RUN VIA LOCAL SOURCE"
echo "================================================================================"

gcloud config set project ${PROJECT_ID}

gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --region=${REGION} \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="DEPLOYMENT_ID=V9-LAFAYETTE-2026-LIVE,SIREN_ISSUER=943610196,BANK_DESTINATION=Hello Balín" \
    --min-instances=1 \
    --max-instances=10 \
    --quiet
