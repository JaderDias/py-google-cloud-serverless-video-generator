provider "google" {
  project = var.project
  region  = var.region
}

resource "google_app_engine_application" "app" {
  project       = var.project
  location_id   = var.location_id
  database_type = "CLOUD_FIRESTORE"
}

resource "google_storage_bucket" "bucket" {
  name    = "${var.project}-bucket"
}

module "save_chess_games" {
  source               = "./modules/function"
  project              = var.project
  function_name        = "save_chess_games"
  function_entry_point = "app"
  pubsub_topic_name    = "save_chess_games_trigger"
  source_bucket_name   = google_storage_bucket.bucket.name
  source_dir           = abspath("../python/save_chess_games")
  depends_on = [
    google_app_engine_application.app,
  ]
}

resource "google_cloud_scheduler_job" "save_chess_games_job" {
  name        = "save_chess_games_job"
  description = "triggers save_chess_games daily"
  schedule    = "30 * * * *"

  pubsub_target {
    topic_name = "projects/${var.project}/topics/save_chess_games_trigger"
    data       = base64encode("test")
  }
  depends_on = [
    module.save_chess_games,
  ]
}

resource "google_firestore_index" "chess_game_index" {
  project = var.project
  collection = "ChessGame"
  fields {
    field_path = "Result"
    order      = "ASCENDING"
  }
  fields {
    field_path = "ScriptId"
    order      = "ASCENDING"
  }
  fields {
    field_path = "HalfMoves"
    order      = "ASCENDING"
  }
  fields {
    field_path = "WhiteElo"
    order      = "DESCENDING"
  }
  depends_on = [
    google_cloud_scheduler_job.save_chess_games_job,
  ]
}

module "chess_to_script" {
  source               = "./modules/function"
  project              = var.project
  function_name        = "chess_to_script"
  function_entry_point = "app"
  pubsub_topic_name    = "chess_to_script_trigger"
  source_bucket_name   = google_storage_bucket.bucket.name
  source_dir           = abspath("../python/chess_to_script")
  depends_on = [
    google_firestore_index.chess_game_index,
  ]
}

resource "google_cloud_scheduler_job" "chess_to_script_job" {
  name        = "chess_to_script_job"
  description = "triggers chess_to_script hourly"
  schedule    = "0 0 * * *"

  pubsub_target {
    topic_name = "projects/${var.project}/topics/chess_to_script_trigger"
    data       = base64encode("test")
  }
  depends_on = [
    module.chess_to_script,
  ]
}
