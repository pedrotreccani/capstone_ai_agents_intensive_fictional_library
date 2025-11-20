#!/bin/bash
set -e

# Configuration
PROJECT_ID="YOUR_PROJECT_ID"
REGION="us-central1"
ZONE="us-central1-a"
CLUSTER_NAME="library-cluster"
DB_INSTANCE_NAME="library-db"
DB_NAME="library"
DB_USER="library_user"
SERVICE_ACCOUNT="library-api"

echo "=== Setting up Library API on GCP ==="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    container.googleapis.com \
    sqladmin.googleapis.com \
    cloudtrace.googleapis.com \
    logging.googleapis.com \
    cloudbuild.googleapis.com

# Create GKE cluster
echo "Creating GKE cluster..."
gcloud container clusters create $CLUSTER_NAME \
    --region=$REGION \
    --num-nodes=1 \
    --machine-type=e2-standard-2 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=5 \
    --enable-autorepair \
    --enable-autoupgrade \
    --workload-pool=$PROJECT_ID.svc.id.goog

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Create Cloud SQL instance
echo "Creating Cloud SQL instance..."
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --backup \
    --backup-start-time=03:00

# Set database password
DB_PASSWORD=$(openssl rand -base64 32)
gcloud sql users set-password postgres \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD

# Create database
gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME

# Create database user
gcloud sql users create $DB_USER \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD

# Create service account for workload identity
echo "Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT \
    --display-name="Library API Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Bind Kubernetes service account to Google service account
kubectl create serviceaccount library-api-sa

gcloud iam service-accounts add-iam-policy-binding \
    $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/library-api-sa]"

# Create database URL secret
DB_CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$DB_CONNECTION_NAME"

kubectl create secret generic library-secrets \
    --from-literal=database-url="$DATABASE_URL"

# Update ConfigMap
kubectl create configmap library-config \
    --from-literal=project-id=$PROJECT_ID

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update kubernetes/deployment.yaml with your PROJECT_ID"
echo "2. Build and push the Docker image:"
echo "   docker build -t gcr.io/$PROJECT_ID/library-api:latest ."
echo "   docker push gcr.io/$PROJECT_ID/library-api:latest"
echo "3. Deploy to Kubernetes:"
echo "   kubectl apply -f kubernetes/deployment.yaml"
echo ""
echo "Or use Cloud Build:"
echo "   gcloud builds submit --config=cloudbuild.yaml"
echo ""
echo "Database connection string has been saved as a Kubernetes secret."
echo "Service account: $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"