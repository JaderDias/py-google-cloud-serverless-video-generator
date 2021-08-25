locals {
    timestamp = formatdate("YYMMDDhhmmss", timestamp())
}

# Compress source code
data "archive_file" "source" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "/tmp/function-${var.function_name}-${local.timestamp}.zip"
}

# Add source code zip to bucket
resource "google_storage_bucket_object" "zip" {
  # Append file MD5 to force bucket to be recreated
  name   = "source.zip#${data.archive_file.source.output_md5}"
  bucket = var.source_bucket_name
  source = data.archive_file.source.output_path
}

# Create Cloud Function
resource "google_cloudfunctions_function" "function" {
  name    = var.function_name
  runtime = "python39"

  available_memory_mb   = 128
  source_archive_bucket = var.source_bucket_name
  source_archive_object = google_storage_bucket_object.zip.name
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = var.pubsub_topic_name
  }
  entry_point = var.function_entry_point
  timeout = 120
}