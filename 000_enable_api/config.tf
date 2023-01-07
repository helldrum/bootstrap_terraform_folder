terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
  backend "gcs" {
    bucket = "terraform_state"
    prefix = "enable_api"
  }
}

provider "google" {
  project = var.project
}

