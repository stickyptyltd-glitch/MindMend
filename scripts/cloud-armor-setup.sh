#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   PROJECT_ID=mindmend-production ./scripts/cloud-armor-setup.sh
#
# Requires: gcloud authenticated with Owner/Editor on the project.

: "${PROJECT_ID:?Set PROJECT_ID}"

POLICY_NAME="mindmend-armor-policy"

echo "Creating Cloud Armor policy: ${POLICY_NAME} (idempotent)"
gcloud compute security-policies describe "$POLICY_NAME" --project "$PROJECT_ID" >/dev/null 2>&1 || \
gcloud compute security-policies create "$POLICY_NAME" \
  --description="MindMend WAF/Rate Limit" \
  --project "$PROJECT_ID"

echo "Adding base rate limit rule (idempotent)"
gcloud compute security-policies rules describe 1000 --security-policy "$POLICY_NAME" --project "$PROJECT_ID" >/dev/null 2>&1 || \
gcloud compute security-policies rules create 1000 \
  --security-policy "$POLICY_NAME" \
  --expression "true" \
  --action rate_based_ban \
  --rate-limit-threshold-count 100 \
  --rate-limit-threshold-interval-sec 60 \
  --ban-duration-sec 600 \
  --ban-threshold-count 200 \
  --ban-threshold-interval-sec 60 \
  --project "$PROJECT_ID"

echo "Done. Attach via BackendConfig 'mindmend-backendconfig' already in k8s/ and Helm chart."

