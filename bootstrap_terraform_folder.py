#!/usr/bin/env pipenv-shebang
# coding:utf8
import sys, os
import argparse
import logging
import re

logging.basicConfig(level=logging.INFO)


def parse_args_or_exit():
    parser = argparse.ArgumentParser(
        description="bootstrap terraform folder and base files."
    )
    parser.add_argument(
        "--tf_folders_path",
        type=str,
        help="the path of the new terraform folder (can be absolute or relative)",
    )

    parser.add_argument(
        "--gcs_backend_name",
        type=str,
        help="the name of the gcs use as remote backend to store tf states.",
    )
    args = parser.parse_args()
    return check_args_valid_or_exit(parser, args)


def check_args_valid_or_exit(parser, args):
    if not args.tf_folders_path:
        logging.error("arg --tf_folders_path is missing, exiting early ...")
        parser.print_help()
        sys.exit(-1)

    if not args.gcs_backend_name:
        logging.error("arg --gcs_backend_name is missing, exiting early ...")
        parser.print_help()
        sys.exit(-1)

    tf_folder_naming_pattern = "^[0-9]{3}_(([a-z])*_){1,}([a-z])*$"
    tf_folder_basename = os.path.basename(args.tf_folders_path)
    pattern = re.compile(tf_folder_naming_pattern)
    if not pattern.match(tf_folder_basename):
        logging.error(
            f"arg --tf_folders_path is not valid, given name {tf_folder_basename} does't respect the naming convention {tf_folder_naming_pattern} (ex 000_enable_api) , exiting early ..."
        )
        sys.exit(-1)

    gcs_name_pattern = "^[0-9a-z_.-]{1,}$"
    gcs_pattern = re.compile(gcs_name_pattern)
    if not gcs_pattern.match(args.gcs_backend_name):
        logging.error(
            f"arg --gcs_backend_name is not valid, given name {args.gcs_backend_name} does't respect the naming convention (only lower case, hyphen, underscore), exiting early ..."
        )
        sys.exit(-1)

    return args


def yes_no_question(question):
    while True:
        print("\n" + question)
        response = input()
        if response.lower() in ["yes", "y"]:
            return True
        if response.lower() in ["no", "n"]:
            return False


def generate_config_file_content(args):
    folder_name_striped_numerotation = os.path.basename(args.tf_folders_path)[4:]
    config_file_content = """terraform {{
  required_providers {{
    google = {{
      source = "hashicorp/google"
    }}
  }}
  backend "gcs" {{
    bucket = "{}"
    prefix = "{}"
  }}
}}

provider "google" {{
  project = var.project
}}

""".format(
        args.gcs_backend_name, folder_name_striped_numerotation
    )
    return config_file_content


def generate_variable_file_content():
    return """variable "project" {}

"""


def print_resume_configuration(tf_folders_path, config_file, variable_content):
    print(
        f"""Folder {tf_folders_path} will be create, with thoses files :

config.tf

{config_file}

variable.tf

{variable_content}
    """
    )


def generate_tf_folder_and_files(args, config_file_content, variable_content):
    logging.info(f"create folder {args.tf_folders_path}")
    os.mkdir(args.tf_folders_path)

    config_file = os.path.join(args.tf_folders_path + "/config.tf")

    with open(config_file, "w") as file:
        file.write(config_file_content)

    variable_file = os.path.join(args.tf_folders_path + "/variables.tf")

    with open(variable_file, "w") as file:
        file.write(variable_content)


def main():
    args = parse_args_or_exit()
    config_file_content = generate_config_file_content(args)
    variable_content = generate_variable_file_content()
    print_resume_configuration(args.tf_folders_path, config_file_content, variable_content)

    if not yes_no_question("Is this configuration correct [y/n] ?"):
        logging.info("ok then, maybe trying again later? ¯\_(ツ)_/¯")
        sys.exit(-1)

    generate_tf_folder_and_files(args, config_file_content, variable_content)
    logging.info("files and folder generated")

if __name__ == "__main__":
    main()
