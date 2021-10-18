#!/bin/sh

# set BILLING_ACCOUNT_ID to one of your billing accounts
BILLING_ACCOUNT_ID=`gcloud beta billing accounts list | grep ACCOUNT_ID | cut -d ' ' -f2 | head -1`

RANDOM_SEED=`tr -dc a-z0-9 </dev/urandom | head -c 10`
PROJECT_ID=video-gen-$RANDOM_SEED

# Create a GCP project
gcloud projects create $PROJECT_ID --name="Chess video generator"

gcloud config set project $PROJECT_ID

gcloud beta billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID

gcloud services enable \
    appengine.googleapis.com \
    cloudbuild.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudscheduler.googleapis.com \
    firestore.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    texttospeech.googleapis.com

./resume-setup.sh