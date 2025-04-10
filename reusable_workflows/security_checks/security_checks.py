import os
import json
import re
import subprocess
import sys


def get_changed_files(merge_base_sha: str, branch_head_sha: str) -> list:
    """
    Get the list of files changed in the current pull request.
    """
    try:
        commit_range = f"{merge_base_sha}..{branch_head_sha}"
        result = subprocess.run(
            ["git", "diff", "--name-only", commit_range],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        changed_files = result.stdout.strip().split("\n")
        return [file for file in changed_files if file]  # Remove empty lines
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        sys.exit(1)


def load_config(config_file: str, repo: str) -> list:
    """
    Load the blacklist rules for the given repository from the config.json file.
    """
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found!")
        sys.exit(1)

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config.get(repo, [])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)


def check_files_against_blacklist(changed_files: list, blacklist_files: list) -> None:
    """
    Check if any changed files match the blacklist rules.
    """
    for file in changed_files:
        for rule in blacklist_files:
            try:
                if re.search(rule, file):  # Use regex to match the rule against the file
                    print(f"No changes allowed to file: {file} (matches blacklist rule: {rule})")
                    sys.exit(1)
            except re.error as e:
                print(f"Invalid regex rule: {rule}. Error: {e}")
                sys.exit(1)

    print("All changed files pass conditions.")


def main():
    # Environment variables
    merge_base_sha = os.getenv("MERGE_BASE_SHA", "HEAD")
    branch_head_sha = os.getenv("BRANCH_HEAD_SHA", "")
    repo = os.getenv("REPO", "")

    if not branch_head_sha or not repo:
        print("Error: BRANCH_HEAD_SHA or REPO environment variable is not set.")
        sys.exit(1)

    # Paths
    config_file = ".github/workflows/config.json"

    # Get changed files
    changed_files = get_changed_files(merge_base_sha, branch_head_sha)
    print(f"Changed files: {changed_files}")

    # Load blacklist rules
    blacklist_files = load_config(config_file, repo)

    if not blacklist_files:
        print(f"No rules found for the repository: {repo}")
        sys.exit(0)

    # Check changed files against blacklist
    check_files_against_blacklist(changed_files, blacklist_files)


if __name__ == "__main__":
    main()