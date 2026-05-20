#!/bin/bash
set -e

PROJECT="nova-assistant-chandra"
REGION="us-central1"
IMAGE="us-central1-docker.pkg.dev/${PROJECT}/nova-repo/nova-assistant"

echo "🔨 Building image..."
docker buildx build --platform linux/amd64 \
  -t ${IMAGE}:latest \
  --push .

echo "📋 Getting correct manifest digest..."
MANIFEST_DIGEST=$(gcloud container images describe \
  ${IMAGE}:latest \
  --format='value(image_summary.fully_qualified_digest)' \
  --project=${PROJECT})
echo "Digest: ${MANIFEST_DIGEST}"

echo "✍️ Signing image with KMS..."
gcloud beta container binauthz attestations sign-and-create \
  --artifact-url="${MANIFEST_DIGEST}" \
  --attestor=nova-attestor \
  --attestor-project=${PROJECT} \
  --keyversion-project=${PROJECT} \
  --keyversion-location=${REGION} \
  --keyversion-keyring=nova-binauthz-keyring \
  --keyversion-key=nova-signing-key \
  --keyversion=1 \
  --project=${PROJECT}

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy nova-assistant \
  --image ${MANIFEST_DIGEST} \
  --platform managed \
  --region ${REGION} \
  --project=${PROJECT} \
  --allow-unauthenticated \
  --service-account=nova-sa@${PROJECT}.iam.gserviceaccount.com \
  --update-secrets=GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest \
  --binary-authorization=default \
  --memory 2Gi \
  --port 8080

echo "✅ Nova deployed successfully with Binary Authorization!"
