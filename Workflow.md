# Databricks Notebook Git Workflow

## Description
The goal of this workflow is to enable developers to checkout and work on a branch containing Databricks notebooks to fix errors, implement features. The changes should be committed to a branch and at a later time, merged into the master branch via Pull Requests or simple merging. 

## Requirements
#### 1. Please install dependencies via `requirements.txt`

#### 2. Please configure the Databricks CLI
The Databricks CLI config:

```config
[DEFAULT]
host = <OLD_WORKSPACE_URL>
token = <OLD_WORKSPACE_TOKEN>
```
`dflow.py` can use arbitrary profiles, so deployment can happen to different Databricks workspaces.

## Workflow
#### 1.	Checkout or use an existing repository local on the developer’s machine. This can be done by any git client. 
```bash
git clone git@github.com:gulyasm/test-etl.git
```

#### 2.	Import the repository into a temporary, working location inside Databricks using the command line utility dflow.
```bash
python dflow.py import -p DEFAULT -i <CHECKED_OUT_REPOSITORY_PATH> -o <NOTEBOOK_FOLDER_LOCATION_ON_DATABRICKS>
```


#### 3.	Modify, develop and test the notebooks on Databricks.

#### 4.	Export the changes from Databricks to the local repository. Overwrite the existing local repository in step 1.
```bash
python dflow.py export -o <CHECKED_OUT_REPOSITORY_PATH> -i <NOTEBOOK_FOLDER_LOCATION_ON_DATABRICKS> -f
```
`-f` stands for overwriting the existing files. If you only want to add new notebooks, feel free to omit it.

#### 5.	Use standard git tools to push the changes to Github. Any git client can be used.
```bash
git add Migration.md && git commit -m "fixes doc"
```
Push changes when done you are ready to share & merge your code.

#### 6.	Changes on the master branch can be deployed to Databricks via Github Actions or another CI/CD pipeline, using the Databricks CLI or with the `dflow.py`. It can overwrite an existing folder. This acts as a deployment/release step. This is automatic. `dflow.py` takes a branch name as a parameter, so any branch can be used to deploy the notebooks. This helps creating dev, staging or canary releases.
```bash
python dflow.py deploy -i <REPO_LOCATION> -b <GIT_BRANCH> --force -o <OUTPUT_ON_DATABRICKS>
```

This approach requires the Databricks CLI to be configured on the developers machine. 
