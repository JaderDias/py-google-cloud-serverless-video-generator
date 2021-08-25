PROJECT_ID=$(jq -r '.resources[0].instances[0].attributes.app_id' terraform/terraform.tfstate)
gcloud beta billing projects unlink $PROJECT_ID
gcloud projects delete $PROJECT_ID
rm -rf terraform/.terraform
rm terraform/.terraform.lock.hcl
rm terraform/terraform.tfstate
rm terraform/terraform.tfstate.backup
