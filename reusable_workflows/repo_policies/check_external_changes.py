import fnmatch
import os
import subprocess
import sys

import github3

from shared.utils import download_gh_file, load_env_vars

EXTERNAL_CONTRIB_BLACKLIST_PATH = ".github/repo_policies/EXTERNAL_CONTRIB_BLACKLIST"

def get_changed_files(merge_base_sha: str, branch_head_sha: str, repo_path: str) -> list[str]:
    """
    Compares the files changed in the current branch to the merge base.
    """
    try:
        commit_range = f"{merge_base_sha}..{branch_head_sha}"
        result = subprocess.run(
            ["git", "diff", "--name-only", commit_range],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
            cwd=repo_path
        )
        changed_files = result.stdout.strip().split("\n")
        return [file for file in changed_files if file]  # Remove empty lines
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        sys.exit(1)


def get_blacklisted_files(repo: github3.github.repo) -> list[str]:
    """
    Loads the config from the repository that contains the list of blacklisted files.
    """
    try:
        config_file = download_gh_file(repo, EXTERNAL_CONTRIB_BLACKLIST_PATH)
    except github3.exceptions.NotFoundError:
        return []
    blacklisted_files = [
        line for line in config_file.splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    return blacklisted_files


def check_files_against_blacklist(changed_files: list, blacklist_files: list) -> None:
    """
    Check if any changed files match the blacklist rules using glob pattern matching.
    """
    violations = []
    for file in changed_files:
        for rule in blacklist_files:
            if fnmatch.fnmatch(file, rule):  # Use glob pattern matching
                violations.append(file)

    if len(violations) > 0:
        print(f"No changes allowed to files: {violations}")
        sys.exit(1)

    else:
        print("All changed files pass conditions.")


def main():
    # Environment variables
    REQUIRED_ENV_VARS = ["REPO", "CHANGED_FILES", "ORG", "GH_TOKEN"]
    env_vars = load_env_vars(REQUIRED_ENV_VARS)
    
    gh = github3.login(token=env_vars["GH_TOKEN"])
    repo = gh.repository(owner=env_vars["ORG"], repository=env_vars["REPO"])

    # Get changed files
    changed_files = env_vars["CHANGED_FILES"].split(",")
    print(f"Changed files: {changed_files}")

    blacklist_files = get_blacklisted_files(repo)

    if blacklist_files == []:
        print("No blacklisted files found found.")
        sys.exit(0)

    # Check changed files against blacklist
    check_files_against_blacklist(changed_files, blacklist_files)


if __name__ == "__main__":
    main()