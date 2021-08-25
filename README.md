# py-google-cloud-serverless-video-generator
Generate videos for chess games from PGN files using Google Cloud Functions

## deployment instructions

1. Ensure you have an active billing account https://console.cloud.google.com/billing

This project was designed to run for free, since it's not scheduled to execute more often than the free tier of the used services allow. But you're going to need to link it to an active billing account anyway.

2. Clone this project into your Google Cloud Shell https://shell.cloud.google.com/

```bash
git clone https://github.com/JaderDias/py-google-cloud-serverless-video-generator.git
cd py-google-cloud-serverless-video-generator
./setup.sh
```