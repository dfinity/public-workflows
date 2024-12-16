# internal-workflows

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
