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
Then update the tag in the workflow `.github/workflows/check_cla_ruleset.yml`.
