# public-workflows

This repository contains a set of internal workflows used at DFINITY. So far this includes:

1. [CLA Workflow](CLA-workflow.md)

This repository is not open to external contributions.

## updating pip requirements
Start a venv:
```
python -m venv .venv
source .venv/bin/activate
```
Install pip-tools and run pip-compile:
```
pip install pip-tools
pip-compile requirements.in --upgrade
```

## Testing and Releasing New Workflows

Use the following steps to test and release new workflow changes:
1. Merge changes to the `develop` branch
1. If one doesn't already exist, set up a new testing workflow that gets applied to the `test-compliant-repository-public` and is pinned to the `develop` branch
1. Test your changes there
1. If the changes are successful, merge `develop` into `master`
