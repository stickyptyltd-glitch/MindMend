#!/bin/bash
#
# collect_state.sh - Collect complete infrastructure state for migration planning
# Usage: ./collect_state.sh
# Output: JSON files in ../artifacts/
#

set -euo pipefail

PROJECT_ID="mindmend-production"
REGION="australia-southeast1"
ZONE="asia-southeast1-a"  # Current cluster location
ARTIFACTS_DIR="$(dirname "$0")/../artifacts"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "MindMend Infrastructure State Collection"
echo "Project: $PROJECT_ID"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================"
echo ""

# Create artifacts directory
mkdir -p "$ARTIFACTS_DIR"

# Function to collect with error handling
collect() {
    local name=$1
    local command=$2
    local output_file="${ARTIFACTS_DIR}/${name}.json"

    echo -n "Collecting ${name}... "
    if eval "$command" > "$output_file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠ (no data or error)${NC}"
        echo "[]" > "$output_file"
    fi
}

# ==============================================================================
# GKE Resources
# ==============================================================================

echo "=== GKE Cluster ==="

collect "gke_clusters" \
    "gcloud container clusters list --project=$PROJECT_ID --format=json"

collect "gke_cluster_details" \
    "gcloud container clusters describe mindmend-cluster --zone=$ZONE --project=$PROJECT_ID --format=json"

# ==============================================================================
# Kubernetes Resources
# ==============================================================================

echo ""
echo "=== Kubernetes Resources ==="

# Get cluster credentials first
echo -n "Authenticating to cluster... "
if gcloud container clusters get-credentials mindmend-cluster --zone=$ZONE --project=$PROJECT_ID > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ (skipping k8s resources)${NC}"
    exit 1
fi

collect "k8s_deployments" \
    "kubectl get deployments --all-namespaces -o json"

collect "k8s_services" \
    "kubectl get services --all-namespaces -o json"

collect "k8s_pods" \
    "kubectl get pods --all-namespaces -o json"

collect "k8s_configmaps" \
    "kubectl get configmaps --all-namespaces -o json"

collect "k8s_secrets_list" \
    "kubectl get secrets --all-namespaces -o json | jq 'del(.items[].data)'"  # Remove secret values

collect "k8s_pvc" \
    "kubectl get pvc --all-namespaces -o json"

collect "k8s_ingress" \
    "kubectl get ingress --all-namespaces -o json"

collect "k8s_nodes" \
    "kubectl get nodes -o json"

# ==============================================================================
# Cloud Run
# ==============================================================================

echo ""
echo "=== Cloud Run ==="

collect "cloudrun_services" \
    "gcloud run services list --region=$REGION --project=$PROJECT_ID --format=json"

collect "cloudrun_jobs" \
    "gcloud run jobs list --region=$REGION --project=$PROJECT_ID --format=json"

# ==============================================================================
# Cloud Functions
# ==============================================================================

echo ""
echo "=== Cloud Functions ==="

collect "cloudfunctions_v1" \
    "gcloud functions list --project=$PROJECT_ID --format=json"

collect "cloudfunctions_v2" \
    "gcloud functions list --gen2 --project=$PROJECT_ID --format=json"

# ==============================================================================
# Cloud Workflows
# ==============================================================================

echo ""
echo "=== Cloud Workflows ==="

collect "workflows" \
    "gcloud workflows list --location=$REGION --project=$PROJECT_ID --format=json"

# ==============================================================================
# Cloud Scheduler
# ==============================================================================

echo ""
echo "=== Cloud Scheduler ==="

collect "scheduler_jobs" \
    "gcloud scheduler jobs list --project=$PROJECT_ID --format=json"

# ==============================================================================
# Pub/Sub
# ==============================================================================

echo ""
echo "=== Pub/Sub ==="

collect "pubsub_topics" \
    "gcloud pubsub topics list --project=$PROJECT_ID --format=json"

collect "pubsub_subscriptions" \
    "gcloud pubsub subscriptions list --project=$PROJECT_ID --format=json"

# ==============================================================================
# Container Images
# ==============================================================================

echo ""
echo "=== Container Images ==="

collect "gcr_images" \
    "gcloud container images list --repository=gcr.io/$PROJECT_ID --project=$PROJECT_ID --format=json"

collect "gcr_mindmend_tags" \
    "gcloud container images list-tags gcr.io/$PROJECT_ID/mindmend-app --limit=50 --format=json"

collect "artifact_registry_repos" \
    "gcloud artifacts repositories list --project=$PROJECT_ID --format=json"

# ==============================================================================
# Cloud Build
# ==============================================================================

echo ""
echo "=== Cloud Build ==="

collect "cloud_builds" \
    "gcloud builds list --limit=50 --project=$PROJECT_ID --format=json"

collect "build_triggers" \
    "gcloud beta builds triggers list --project=$PROJECT_ID --format=json"

# ==============================================================================
# IAM & Security
# ==============================================================================

echo ""
echo "=== IAM & Security ==="

collect "service_accounts" \
    "gcloud iam service-accounts list --project=$PROJECT_ID --format=json"

collect "secrets_list" \
    "gcloud secrets list --project=$PROJECT_ID --format=json"

# ==============================================================================
# Networking
# ==============================================================================

echo ""
echo "=== Networking ==="

collect "compute_addresses" \
    "gcloud compute addresses list --project=$PROJECT_ID --format=json"

collect "firewall_rules" \
    "gcloud compute firewall-rules list --project=$PROJECT_ID --format=json"

collect "load_balancers" \
    "gcloud compute forwarding-rules list --project=$PROJECT_ID --format=json"

# ==============================================================================
# Vertex AI
# ==============================================================================

echo ""
echo "=== Vertex AI ==="

collect "vertex_models" \
    "gcloud ai models list --region=$REGION --project=$PROJECT_ID --format=json"

collect "vertex_endpoints" \
    "gcloud ai endpoints list --region=$REGION --project=$PROJECT_ID --format=json"

# ==============================================================================
# Monitoring & Logging
# ==============================================================================

echo ""
echo "=== Monitoring & Logging ==="

collect "monitoring_dashboards" \
    "gcloud monitoring dashboards list --project=$PROJECT_ID --format=json"

collect "logging_sinks" \
    "gcloud logging sinks list --project=$PROJECT_ID --format=json"

collect "recent_errors" \
    "gcloud logging read 'severity>=ERROR' --limit=100 --project=$PROJECT_ID --format=json"

# ==============================================================================
# Quotas
# ==============================================================================

echo ""
echo "=== Quotas ==="

collect "compute_quotas" \
    "gcloud compute project-info describe --project=$PROJECT_ID --format=json | jq '.quotas'"

# ==============================================================================
# Generate Summary
# ==============================================================================

echo ""
echo "=== Generating Summary ==="

cat > "${ARTIFACTS_DIR}/summary.txt" << EOF
MindMend Infrastructure State Collection
=========================================

Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Project: $PROJECT_ID
Region: $REGION
Zone: $ZONE

Collected Files:
$(ls -lh "$ARTIFACTS_DIR" | tail -n +2)

Quick Stats:
- GKE Clusters: $(jq length "${ARTIFACTS_DIR}/gke_clusters.json" 2>/dev/null || echo "N/A")
- K8s Deployments: $(jq '.items | length' "${ARTIFACTS_DIR}/k8s_deployments.json" 2>/dev/null || echo "N/A")
- K8s Services: $(jq '.items | length' "${ARTIFACTS_DIR}/k8s_services.json" 2>/dev/null || echo "N/A")
- K8s Pods: $(jq '.items | length' "${ARTIFACTS_DIR}/k8s_pods.json" 2>/dev/null || echo "N/A")
- Cloud Run Services: $(jq length "${ARTIFACTS_DIR}/cloudrun_services.json" 2>/dev/null || echo "N/A")
- Cloud Functions: $(jq length "${ARTIFACTS_DIR}/cloudfunctions_v2.json" 2>/dev/null || echo "N/A")
- Container Images: $(jq length "${ARTIFACTS_DIR}/gcr_mindmend_tags.json" 2>/dev/null || echo "N/A")
- Service Accounts: $(jq length "${ARTIFACTS_DIR}/service_accounts.json" 2>/dev/null || echo "N/A")
- Secrets: $(jq length "${ARTIFACTS_DIR}/secrets_list.json" 2>/dev/null || echo "N/A")

Next Steps:
1. Review summary.txt and all JSON files in artifacts/
2. Identify AI-related services and dependencies
3. Plan Gemini migration based on current state
4. Create staging environment matching production

EOF

cat "${ARTIFACTS_DIR}/summary.txt"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Collection complete!${NC}"
echo -e "${GREEN}Artifacts saved to: $ARTIFACTS_DIR${NC}"
echo -e "${GREEN}================================================${NC}"

# Generate human-readable reports
echo ""
echo "Generating human-readable reports..."

# Deployment summary
cat > "${ARTIFACTS_DIR}/deployments_summary.txt" << EOF
Kubernetes Deployments Summary
===============================

$(kubectl get deployments --all-namespaces 2>/dev/null | head -20 || echo "Unable to fetch")

EOF

# Service summary
cat > "${ARTIFACTS_DIR}/services_summary.txt" << EOF
Kubernetes Services Summary
============================

$(kubectl get services --all-namespaces 2>/dev/null | head -20 || echo "Unable to fetch")

EOF

echo "Done! Review the following files:"
echo "  - ${ARTIFACTS_DIR}/summary.txt"
echo "  - ${ARTIFACTS_DIR}/deployments_summary.txt"
echo "  - ${ARTIFACTS_DIR}/services_summary.txt"
echo "  - ${ARTIFACTS_DIR}/*.json (detailed data)"
