import argparse
import subprocess
import tempfile
from typing import List

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=["import", "export", "deploy"], help="The command to run")
parser.add_argument("-o", "--output", dest="output", required=False, help="The output path")
parser.add_argument("-i", "--input", dest="input", default=".", required=False, help="The input path")
parser.add_argument("-f", "--force", dest="force", action="store_true", help="To overwrite existing ")
parser.add_argument("-b", "--branch", dest="branch", help="The branch to be deployed. Only applicable with `deploy`")
parser.add_argument("-p", "--profile", dest="profile", help="The profile from the Databricks CLI to be used")
args = parser.parse_args()


def add_profile(commands: List[str], profile: str) -> None:
  commands.extend(["--profile", profile])


def add_force(commands: List[str]) -> None:
    commands.append("-o")


if args.command == "import":
    arguments = ['databricks', 'workspace', 'import_dir', args.input,
                    args.output, "-e"]
    if args.force:
      add_force(arguments)
    if args.profile:
      add_profile(arguments, args.profile)
    subprocess.run(arguments,  encoding="utf-8")

if args.command == "export":
    arguments = ['databricks', 'workspace', 'export_dir', args.input,
                    args.output]
    if args.force:
      add_force(arguments)
    if args.profile:
      add_profile(arguments, args.profile)
    subprocess.run(arguments,  encoding="utf-8")

if args.command == "deploy":
    with tempfile.TemporaryDirectory() as tmpdir:
      subprocess.run(["git", "clone", "--branch", args.branch, args.input, tmpdir])
      arguments = ['databricks', 'workspace',
                   'import_dir', tmpdir, args.output, "-e"]
      if args.force:
        add_force(arguments)
      if args.profile:
        add_profile(arguments, args.profile)
      subprocess.run(arguments,  encoding="utf-8")