#!/bin/sh

if [ -f "terraform/terraform.tfstate" ]; then
	PROJECT_ID=$(jq -r '.resources[0].instances[0].attributes.app_id' terraform/terraform.tfstate)
    gcloud config set project $PROJECT_ID
else
    echo "no terraform state file"
fi