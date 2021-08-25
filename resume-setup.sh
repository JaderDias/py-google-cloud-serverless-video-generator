#!/bin/sh

./set-project.sh

PROJECT_ID=$(gcloud config get-value project)

cd terraform

terraform init

terraform plan --var "project=$PROJECT_ID"

terraform apply --var "project=$PROJECT_ID"
