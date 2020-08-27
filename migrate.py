import os
import requests
import subprocess
import json
import argparse
from typing import List, Tuple

CLUSTER_REQ_ELEMENTS = ["num_workers", "autoscale", "cluster_name", "spark_version", "spark_conf", "node_type_id",
                        "driver_node_type_id", "custom_tags", "cluster_log_conf", "spark_env_vars", "autotermination_minutes", "enable_elastic_disk"]


def create_user(username: str, new_url: str, new_token: str):
    endpoint = "/preview/scim/v2/Users"
    data = {
        "schemas": [
            "urn:ietf:params:scim:schemas:core:2.0:User"
        ],
        "userName": username
    }
    header = {
        'Authorization': f"Bearer {new_token}",
        'Content-Type': 'application/scim+json'
    }
    r = requests.post(f"{new_url}{endpoint}",
                      headers=header, data=json.dumps(data))


def list_users():
    for u in get_users():
        print(u)


def get_users():
    process = subprocess.run(['databricks', 'workspace', 'ls', '/Users', "--profile", "DEFAULT"],
                             encoding="utf-8", capture_output=True)
    return process.stdout.strip().split("\n")


def migrate_root(
        outputpath: str = None, 
        force: bool = False, 
        temppath: str = None,
        old_profile: str = None,
        new_profile: str = None):
    process = subprocess.check_output(
        ["databricks", "workspace", "list", "--profile", old_profile], encoding="utf-8")
    exclude = ["Users", "Shared"]
    folders = [f.strip() for f in process.split("\n")
               if f.strip() not in exclude]
    clean_folders = ["/" + f for f in folders if f.strip()]
    folder = f"{temppath}/notebooks/root/"
    os.makedirs(folder, exist_ok=True)
    outputpath = outputpath if outputpath else "/"
    for f in clean_folders:
        local_current_output = os.path.join(folder, f[1:])
        export_arguments = ['databricks', 'workspace', 'export_dir', local_current_output,
                            os.path.join(outputpath, f[1:]), "--profile", new_profile]
        if force:
            export_arguments.append("-o")
        subprocess.run(['databricks', 'workspace', 'export_dir',
                        f, local_current_output, "--profile", new_profile],  encoding="utf-8")
        subprocess.run(export_arguments,  encoding="utf-8")


def migrate_users(
        users: List[str],
        base_path,
        skip_user_creation: bool = False,
        new_url: str = None,
        new_token: str = None,
        temppath: str = None,
        old_profile: str = None,
        new_profile: str = None):

    for u in users:
        print(f"Migrating {u}")
        if not skip_user_creation:
            print(f"Creating {u}")
            create_user(u, new_url, new_token)
        folder = f"{temppath}/notebooks/{u}"
        os.makedirs(folder)
        outputpath = os.path.join(base_path, u) if base_path else f"/Users/{u}"
        subprocess.run(['databricks', 'workspace', 'export_dir',
                        f"/Users/{u}", folder, "--profile", old_profile],  encoding="utf-8")
        subprocess.run(['databricks', 'workspace', 'import_dir', folder,
                        outputpath, "--profile", new_profile],  encoding="utf-8")


def migrate_cluster(cluster, old_profile: str, new_profile: str) -> str:
    process = subprocess.run(["databricks", "clusters", "get", "--cluster-id",
                              cluster, "--profile", old_profile], encoding="utf-8", capture_output=True)
    config = json.loads(process.stdout)
    cluster_json_keys = config.keys()
    for key in list(cluster_json_keys):
        if key not in CLUSTER_REQ_ELEMENTS:
            config.pop(key, None)
    cluster_create_out = subprocess.check_output(
        ["databricks", "clusters", "create",  "--json", json.dumps(config), "--profile", new_profile])
    response = json.loads(cluster_create_out)
    new_id = response["cluster_id"]
    subprocess.run(["databricks", "clusters", "delete",  "--cluster-id",
                    new_id, "--profile", new_profile], encoding="utf-8")
    return new_id


def migrate_clusters(old_profile:str, new_profile: str) -> List[Tuple[str, str]]:
    process = subprocess.run(['databricks', 'clusters', 'list', "--profile",
                              old_profile],  encoding="utf-8", capture_output=True)

    def clean_cluster(x): return [l.strip() for l in x if l.strip()]
    clusters = [clean_cluster(cl.split(" "))
                for cl in process.stdout.split("\n") if cl]
    interactive_clusters = [l[0]
                            for l in clusters if not l[1].startswith("job-")]
    mapped_clusters = []
    for c in interactive_clusters:
        new_id = migrate_cluster(c, old_profile, new_profile)
        print(f"Migrated {c} to {new_id}")
        mapped_clusters.append((c, new_id))
    return mapped_clusters


parser = argparse.ArgumentParser()
parser.add_argument("command", choices=[
                    "list-users", "migrate-users", "migrate-root-notebooks", "migrate-clusters"])
parser.add_argument("-l", "--userlist", help="List of users to migrate")
parser.add_argument("-c", "--config", dest="config",
                    help="The config file to use")

args = vars(parser.parse_args())
with open(args["config"], "r") as f:
    config = json.loads(f.read())
    args.update(config)

if args.command == "list-users":
    list_users()

if args.command == "migrate-users":
    with open(args["userlist"], "r") as f:
        users = [l.strip() for l in f.readlines()]
    migrate_users(users, args["outputpath"], skip_user_creation=args["skipusers"], temppath=args["temppath"],
                  new_token=config["new-workspace-token"], new_url=config["new-workspace-url"])

if args.command == "migrate-root-notebooks":
    migrate_root(outputpath=args["outputpath"],
                 force=args["force"], temppath=args["temppath"])

if args.command == "migrate-clusters":
    _ = migrate_clusters()
