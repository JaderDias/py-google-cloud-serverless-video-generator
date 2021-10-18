#!/bin/sh

./set-project.sh

PROJECT_ID=$(gcloud config get-value project)

cd terraform

terraform init

terraform apply --var "project=$PROJECT_ID"
