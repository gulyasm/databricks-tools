# Migration Documentation

## Requirements


#### 1. Install dependencies from `requirements.txt`


#### 2. Configure the old and new profiles for Databricks CLI. 
The Databricks CLI config:

```config
[<OLD_WORKSPACE_PROFILE>]
host = <OLD_WORKSPACE_URL>
token = <OLD_WORKSPACE_TOKEN>

[<NEW_WORKSPACE_PROFILE>]
host = <NEW_WORKSPACE_URL>
token = <NEW_WORKSPACE_TOKEN>
```
The profile names can be anything


#### 3. Configure migration script (`config.json`):
```json
{
    "temppath": "<TEMPPATH>",
    "output-path": "<OUTPATH>",
    "force": true,
    "new-workspace-url": "<NEW_WORKSPACE_URL>",
    "new-workspace-token": "<NEW_WORKSPACE_TOKEN>",
    "skip-users": <true | false>,
    "new-profile": "<NEW_WORKSPACE_PROFILE>",
    "old-profile": "<OLD_WORKSPACE_PROFILE>"
}

```

- `temppath`: The local path where the script will save the exported notebooks before uploading to the new workspace
- `output-path`: If set, the output path for the notebooks on the new workspace. If not set, user noteboooks will be uploaded to the new User folders
- `force`: Overwrite existing notebooks when importing
- `new-workspace-url`: For creating users, the script needs the URL of the new workspace
- `new-workspace-url`: For creating users, the script needs a user token of the new workspace
- `skip-users` Don't create the user accounts on the new workspace when migrating the users
- `new-profile`: The new workspace profile in the Databricks CLI config
- `old-profile`: The old workspace profile in the Databricks CLI config



#### 4. Run the migration script:
  - migrate-users: Migrate Users and their notebooks
  - migrate-clusters: Migrate interactive cluster configurations. Creates and terminates clusters. If the new clusters are idle for 90 days, they will be deleted. Doesn't work on cross-cloud migrations.
  - migrate-root: Migrate notebooks on the workspace root. Doesn't migrate `Users` and `Shared`
