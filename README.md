# internal-workflows

This repository contains a set of internal workflows used at DFINITY. So far this includes:

1. [CLA Workflow](CLA-workflow.md)

This repository is not open to external contributions.

## Updating the workflow

If a new change needs to be deployed a new tag needs to be created. Currently this process is not automatated, so you need to run:
```
git tag <tagname>
git push origin --tags
```
This will allow you to test out the workflow first if you'd like (we have a ruleset called CLA check (dev)), otherwise update the main ruleset CLA-check with the correct tag.
