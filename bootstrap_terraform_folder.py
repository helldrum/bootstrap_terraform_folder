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


def check_arg_exist_or_exit(parser, arg, arg_name):
    if not arg:
        logging.error(f"arg --{arg_name} is missing, exiting early ...")
        parser.print_help()
        sys.exit(-1)


def check_string_match_pattern_or_exist(pattern, string_to_match, error_message):
    pattern = re.compile(pattern)
    if not pattern.match(string_to_match):
        logging.error(error_message)
        sys.exit(-1)


def check_args_valid_or_exit(parser, args):
    check_arg_exist_or_exit(parser, args.tf_folders_path, "tf_folders_path")
    check_arg_exist_or_exit(parser, args.gcs_backend_name, "gcs_backend_name")

    tf_folder_naming_pattern = "^[0-9]{3}_(([a-z])*_){1,}([a-z])*$"
    tf_folder_basename = os.path.basename(args.tf_folders_path)
    error_message = f"arg --tf_folders_path is not valid, given name {tf_folder_basename} does't respect the naming convention {tf_folder_naming_pattern} (ex 000_enable_api) , exiting early ..."
    check_string_match_pattern_or_exist(
        tf_folder_naming_pattern, tf_folder_basename, error_message
    )

    gcs_naming_pattern = "^[0-9a-z_.-]{1,}$"
    error_message = f"arg --gcs_backend_name is not valid, given name {args.gcs_backend_name} does't respect the naming convention (only lower case, hyphen, underscore), exiting early ..."
    check_string_match_pattern_or_exist(
        gcs_naming_pattern, args.gcs_backend_name, error_message
    )

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


def write_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)


def generate_tf_folder_and_files(args, config_file_content, variable_content):
    logging.info(f"create folder {args.tf_folders_path}")
    
    try:
        os.mkdir(args.tf_folders_path)
    except FileExistsError:
        logging.error(f"folder {args.tf_folders_path} already exist, skip creation and exist early ...")
        sys.exit(-1)

    config_file = os.path.join(args.tf_folders_path + "/config.tf")
    variable_file = os.path.join(args.tf_folders_path + "/variables.tf")

    write_file(config_file, config_file_content)
    write_file(variable_file, variable_content)


def main():
    args = parse_args_or_exit()
    config_file_content = generate_config_file_content(args)
    variable_content = generate_variable_file_content()
    print_resume_configuration(
        args.tf_folders_path, config_file_content, variable_content
    )

    if not yes_no_question("Is this configuration correct [y/n] ?"):
        logging.info("ok then, maybe trying again later? ¯\_(ツ)_/¯")
        sys.exit(-1)

    generate_tf_folder_and_files(args, config_file_content, variable_content)
    logging.info("files and folder generated")


if __name__ == "__main__":
    main()
