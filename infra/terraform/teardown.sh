#!/usr/bin/env bash
#
# teardown.sh — Destroy all "Can I Click It?" AWS infrastructure
#
# Usage:
#   ./teardown.sh                  # Teardown dev only (default)
#   ./teardown.sh dev              # Teardown dev only
#   ./teardown.sh prod             # Teardown prod only
#   ./teardown.sh all              # Teardown both dev and prod
#   ./teardown.sh all --include-state  # Teardown everything + state bucket + lock table
#
# Prerequisites:
#   - AWS CLI v2 configured (aws sts get-caller-identity works)
#   - Terraform >= 1.5.0
#   - Correct AWS_PROFILE set (e.g. export AWS_PROFILE=lemon)

set -euo pipefail

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
PROJECT="clickit"
REGION="us-east-1"
STATE_BUCKET="clickit-terraform-state"
LOCK_TABLE="clickit-terraform-locks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVS_DIR="$SCRIPT_DIR/environments"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
log()   { echo -e "${CYAN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }

confirm() {
    local msg="$1"
    echo ""
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  WARNING: THIS ACTION IS DESTRUCTIVE AND IRREVERSIBLE  ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "$msg"
    echo ""
    read -rp "Type 'destroy' to confirm: " answer
    if [[ "$answer" != "destroy" ]]; then
        log "Aborted."
        exit 0
    fi
}

# -------------------------------------------------------------------
# Pre-flight checks
# -------------------------------------------------------------------
preflight() {
    log "Running pre-flight checks..."

    if ! command -v aws &>/dev/null; then
        err "AWS CLI not found. Install it first."
        exit 1
    fi

    if ! command -v terraform &>/dev/null; then
        err "Terraform not found. Install it first."
        exit 1
    fi

    if ! aws sts get-caller-identity &>/dev/null; then
        err "AWS credentials not configured. Set AWS_PROFILE or run 'aws configure'."
        exit 1
    fi

    local account_id account_arn
    account_id=$(aws sts get-caller-identity --query 'Account' --output text)
    account_arn=$(aws sts get-caller-identity --query 'Arn' --output text)

    echo ""
    log "AWS Account: ${YELLOW}${account_id}${NC}"
    log "AWS Role:    $account_arn"
    log "AWS Profile: ${AWS_PROFILE:-<default>}"
    log "AWS Region:  $REGION"
    log "Project:     $PROJECT"
    echo ""

    read -rp "Is this the correct AWS account? (y/N): " acct_confirm
    if [[ "$acct_confirm" != "y" && "$acct_confirm" != "Y" ]]; then
        err "Wrong account. Set the correct profile: export AWS_PROFILE=<profile>"
        exit 1
    fi
}

# -------------------------------------------------------------------
# Scale ECS services to zero (graceful shutdown)
# -------------------------------------------------------------------
scale_down_services() {
    local env="$1"
    local cluster="${PROJECT}-${env}-cluster"

    log "Scaling down ECS services in cluster: $cluster"

    # Check if cluster exists
    if ! aws ecs describe-clusters --region "$REGION" --clusters "$cluster" \
         --query 'clusters[?status==`ACTIVE`].clusterName' --output text 2>/dev/null | grep -q "$cluster"; then
        warn "Cluster $cluster not found or inactive. Skipping scale-down."
        return 0
    fi

    local services
    services=$(aws ecs list-services --region "$REGION" --cluster "$cluster" \
               --query 'serviceArns[*]' --output text 2>/dev/null || true)

    if [[ -z "$services" || "$services" == "None" ]]; then
        warn "No services found in $cluster."
        return 0
    fi

    for svc_arn in $services; do
        local svc_name
        svc_name=$(echo "$svc_arn" | awk -F'/' '{print $NF}')
        log "  Scaling $svc_name to 0..."
        aws ecs update-service --region "$REGION" --cluster "$cluster" \
            --service "$svc_name" --desired-count 0 --no-cli-pager >/dev/null 2>&1 || true
    done

    log "  Waiting for tasks to drain (30s)..."
    sleep 30
    ok "Services scaled to zero in $cluster."
}

# -------------------------------------------------------------------
# Clean ECR repositories (delete all images)
# -------------------------------------------------------------------
clean_ecr() {
    log "Cleaning ECR repositories..."

    local repos=("${PROJECT}/api" "${PROJECT}/frontend")

    for repo in "${repos[@]}"; do
        if aws ecr describe-repositories --region "$REGION" --repository-names "$repo" &>/dev/null; then
            local images
            images=$(aws ecr list-images --region "$REGION" --repository-name "$repo" \
                     --query 'imageIds[*]' --output json 2>/dev/null)

            if [[ "$images" != "[]" && -n "$images" ]]; then
                log "  Deleting images from $repo..."
                aws ecr batch-delete-image --region "$REGION" --repository-name "$repo" \
                    --image-ids "$images" --no-cli-pager >/dev/null 2>&1 || true
                ok "  Cleaned $repo."
            else
                warn "  No images in $repo."
            fi
        else
            warn "  ECR repo $repo not found. Skipping."
        fi
    done
}

# -------------------------------------------------------------------
# Delete CloudWatch log groups that Terraform might miss
# -------------------------------------------------------------------
clean_log_groups() {
    local env="$1"
    log "Cleaning CloudWatch log groups for $env..."

    local prefixes=("/ecs/${PROJECT}-${env}-api" "/ecs/${PROJECT}-${env}-frontend" "/ecs/${PROJECT}-${env}-migration")

    for prefix in "${prefixes[@]}"; do
        if aws logs describe-log-groups --region "$REGION" --log-group-name-prefix "$prefix" \
           --query 'logGroups[*].logGroupName' --output text 2>/dev/null | grep -q "$prefix"; then
            log "  Deleting log group: $prefix"
            aws logs delete-log-group --region "$REGION" --log-group-name "$prefix" 2>/dev/null || true
        fi
    done
}

# -------------------------------------------------------------------
# Terraform destroy for an environment
# -------------------------------------------------------------------
terraform_destroy() {
    local env="$1"
    local env_dir="$ENVS_DIR/$env"

    if [[ ! -d "$env_dir" ]]; then
        warn "Environment directory not found: $env_dir. Skipping."
        return 0
    fi

    log "Running terraform destroy for: $env"
    cd "$env_dir"

    # Init (in case .terraform is missing)
    log "  Initializing Terraform..."
    if ! terraform init -input=false -reconfigure 2>&1 | tail -1; then
        warn "  Terraform init failed for $env. State bucket may not exist."
        cd "$SCRIPT_DIR"
        return 0
    fi

    # Destroy
    log "  Destroying resources (this may take 10-15 minutes)..."
    if terraform destroy -auto-approve -input=false 2>&1; then
        ok "Terraform destroy complete for $env."
    else
        err "Terraform destroy failed for $env. Some resources may need manual cleanup."
        err "Check the AWS console for remaining resources tagged Project=$PROJECT, Environment=$env"
    fi

    # Clean up local Terraform files
    rm -rf .terraform .terraform.lock.hcl

    cd "$SCRIPT_DIR"
}

# -------------------------------------------------------------------
# Delete Terraform state infrastructure
# -------------------------------------------------------------------
destroy_state_infra() {
    log "Destroying Terraform state infrastructure..."

    # Empty and delete S3 state bucket
    # head-bucket returns non-zero for both 403 (wrong account) and 404 (not found).
    # Capture stderr to distinguish the two cases.
    local hb_err
    hb_err=$(aws s3api head-bucket --bucket "$STATE_BUCKET" 2>&1) && hb_err=""
    if [[ -n "$hb_err" && "$hb_err" == *"403"* ]]; then
        err "Access denied for bucket $STATE_BUCKET. Are you using the correct AWS_PROFILE?"
        err "Current profile: ${AWS_PROFILE:-<default>}"
        return 1
    fi
    if [[ -z "$hb_err" ]]; then
        log "  Emptying state bucket: $STATE_BUCKET"
        aws s3 rm "s3://$STATE_BUCKET" --recursive --region "$REGION" 2>/dev/null || true

        # Delete versioned objects too
        local versions
        versions=$(aws s3api list-object-versions --bucket "$STATE_BUCKET" \
                   --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
                   --output json 2>/dev/null || echo '{"Objects": []}')

        if [[ $(echo "$versions" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('Objects') or []))" 2>/dev/null) -gt 0 ]]; then
            log "  Deleting versioned objects..."
            aws s3api delete-objects --bucket "$STATE_BUCKET" --delete "$versions" \
                --region "$REGION" --no-cli-pager >/dev/null 2>&1 || true
        fi

        # Delete markers
        local markers
        markers=$(aws s3api list-object-versions --bucket "$STATE_BUCKET" \
                  --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
                  --output json 2>/dev/null || echo '{"Objects": []}')

        if [[ $(echo "$markers" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('Objects') or []))" 2>/dev/null) -gt 0 ]]; then
            log "  Deleting delete markers..."
            aws s3api delete-objects --bucket "$STATE_BUCKET" --delete "$markers" \
                --region "$REGION" --no-cli-pager >/dev/null 2>&1 || true
        fi

        log "  Deleting state bucket: $STATE_BUCKET"
        aws s3api delete-bucket --bucket "$STATE_BUCKET" --region "$REGION" 2>/dev/null || true
        ok "State bucket deleted."
    else
        warn "State bucket $STATE_BUCKET not found."
    fi

    # Delete DynamoDB lock table
    local ddb_err
    ddb_err=$(aws dynamodb describe-table --table-name "$LOCK_TABLE" --region "$REGION" 2>&1) && ddb_err=""
    if [[ -n "$ddb_err" && "$ddb_err" == *"AccessDeniedException"* ]]; then
        err "Access denied for DynamoDB table $LOCK_TABLE. Are you using the correct AWS_PROFILE?"
        return 1
    fi
    if [[ -z "$ddb_err" ]]; then
        log "  Deleting lock table: $LOCK_TABLE"
        aws dynamodb delete-table --table-name "$LOCK_TABLE" --region "$REGION" --no-cli-pager >/dev/null 2>&1 || true
        ok "Lock table deleted."
    else
        warn "Lock table $LOCK_TABLE not found."
    fi
}

# -------------------------------------------------------------------
# Teardown a single environment
# -------------------------------------------------------------------
teardown_env() {
    local env="$1"
    log "=========================================="
    log "  Tearing down: $env"
    log "=========================================="

    scale_down_services "$env"
    clean_ecr
    terraform_destroy "$env"
    clean_log_groups "$env"

    ok "Teardown complete for $env."
}

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
main() {
    local target="${1:-dev}"
    local include_state=false

    # Parse flags
    for arg in "$@"; do
        if [[ "$arg" == "--include-state" ]]; then
            include_state=true
        fi
    done

    preflight

    case "$target" in
        dev)
            confirm "This will destroy ALL dev infrastructure for ${PROJECT}.\n  - ECS services, tasks, cluster\n  - ALB, target groups\n  - RDS PostgreSQL database (ALL DATA WILL BE LOST)\n  - ElastiCache Redis\n  - ECR images\n  - Secrets Manager secrets\n  - VPC, subnets, NAT gateway\n  - S3 data bucket\n  - CloudWatch log groups\n  - IAM roles and policies"
            teardown_env "dev"
            ;;
        prod)
            confirm "This will destroy ALL prod infrastructure for ${PROJECT}.\n  - ECS services, tasks, cluster\n  - ALB, target groups, WAF\n  - RDS PostgreSQL database (ALL DATA WILL BE LOST)\n  - ElastiCache Redis\n  - ECR images\n  - Secrets Manager secrets\n  - VPC, subnets, NAT gateways\n  - S3 data + ALB logs buckets\n  - CloudWatch log groups, alarms\n  - IAM roles and policies\n  - Auto-scaling policies"
            teardown_env "prod"
            ;;
        all)
            local state_msg=""
            if $include_state; then
                state_msg="\n  - Terraform state bucket (${STATE_BUCKET})\n  - DynamoDB lock table (${LOCK_TABLE})"
            fi
            confirm "This will destroy ALL infrastructure for ${PROJECT} in BOTH dev and prod.${state_msg}\n\n  Everything listed above for both environments will be permanently deleted."
            teardown_env "dev"
            teardown_env "prod"
            if $include_state; then
                destroy_state_infra
            fi
            ;;
        *)
            err "Unknown target: $target"
            echo "Usage: $0 [dev|prod|all] [--include-state]"
            exit 1
            ;;
    esac

    echo ""
    ok "=========================================="
    ok "  Teardown finished!"
    ok "=========================================="
    echo ""
    log "Verify in the AWS console that no resources remain:"
    log "  https://console.aws.amazon.com/ecs/home?region=${REGION}#/clusters"
    log "  https://console.aws.amazon.com/rds/home?region=${REGION}#databases:"
    log "  https://console.aws.amazon.com/vpc/home?region=${REGION}#vpcs:"
}

main "$@"
