import fnmatch
import os
import subprocess
import sys

import github3

from shared.utils import download_gh_file

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
    for file in changed_files:
        for rule in blacklist_files:
            if fnmatch.fnmatch(file, rule):  # Use glob pattern matching
                print(f"No changes allowed to file: {file} (matches blacklist rule: {rule})")
                os.system(f"""echo 'close_pr=true' >> $GITHUB_OUTPUT""")
                sys.exit(0)

    print("All changed files pass conditions.")


def main():
    # Environment variables
    merge_base_sha = os.getenv("MERGE_BASE_SHA", "HEAD")
    branch_head_sha = os.getenv("BRANCH_HEAD_SHA", "")
    repo = os.getenv("REPO", "")
    repo_path = os.getenv("REPO_PATH", "current-repo")
    org = os.getenv("ORG", "dfinity")
    gh_token = os.getenv("GH_TOKEN", "")

    if not branch_head_sha or not repo:
        print("Error: BRANCH_HEAD_SHA or REPO environment variable is not set.")
        sys.exit(1)
    
    gh = github3.login(token=gh_token)
    repo = gh.repository(owner=org, repository=repo)

    # Get changed files
    changed_files = get_changed_files(merge_base_sha, branch_head_sha, repo_path)
    print(f"Changed files: {changed_files}")

    blacklist_files = get_blacklisted_files(repo)

    if blacklist_files == []:
        print(f"No blacklisted files found found.")
        os.system(f"""echo 'close_pr=false' >> $GITHUB_OUTPUT""")
        sys.exit(0)

    # Check changed files against blacklist
    check_files_against_blacklist(changed_files, blacklist_files)


if __name__ == "__main__":
    main()