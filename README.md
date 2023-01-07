# bootstrap_terraform_folder

This tool is mean to create a terraform gcp squeleton folder, creating backend file with gcs remote, variables.tf with project variable.

# usage

```
usage: bootstrap_terraform_folder.py [-h] [--tf_folders_path TF_FOLDERS_PATH] [--gcs_backend_name GCS_BACKEND_NAME]

bootstrap terraform folder and base files.

options:
  -h, --help            show this help message and exit
  --tf_folders_path TF_FOLDERS_PATH
                        the path of the new terraform folder (can be absolute or relative)
  --gcs_backend_name GCS_BACKEND_NAME
                        the name of the gcs use as remote backend to store tf states.

example:

./bootstrap_terraform_folder.py --tf_folders_path=000_enable_api --gcs_backend_name=terraform_state
Folder 000_enable_api will be create, with thoses files :

config.tf

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



variable.tf

variable "project" {}


    

Is this configuration correct [y/n] ?
y
INFO:root:create folder 000_enable_api
INFO:root:files and folder generated
```
