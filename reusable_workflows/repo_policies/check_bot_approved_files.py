import fnmatch
import subprocess
from typing import Optional

import github3

from shared.utils import download_gh_file, load_env_vars

BOT_APPROVED_FILES_PATH = ".github/repo_policies/BOT_APPROVED_FILES"
REQUIRED_ENV_VARS = ["CHANGED_FILES", "USER", "GH_TOKEN", "GH_ORG", "REPO"]


def get_approved_files_config(repo: github3.github.repo) -> str:
    """
    Loads the config from the repository that contains the list of approved files.
    """
    try:
        config_file = download_gh_file(repo, BOT_APPROVED_FILES_PATH)
        return config_file
    except github3.exceptions.NotFoundError:
        raise Exception(
            f"No config file found. Make sure you have a file saved at {BOT_APPROVED_FILES_PATH} in the default branch"
        )

def get_approved_files(repo: github3.github.repo) -> list[str]:
    """
    Extracts the list of approved files from the config file.
    """
    config_file = get_approved_files_config(repo)
    approved_files = [
        line for line in config_file.splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    return approved_files

def check_files_in_approved_list(changed_files: list[str], approved_files: list[str]) -> bool:
    """
    Checks if all the changed files are in the list of approved files.
    """
    return all(
        any(fnmatch.fnmatch(changed_file, pattern) for pattern in approved_files)
        for changed_file in changed_files
    )


def check_if_pr_is_blocked(env_vars: dict) -> None:
    """
    Logic to check if the Bot's PR can be merged or should be blocked.
    """
    gh = github3.login(token=env_vars["GH_TOKEN"])
    repo = gh.repository(owner=env_vars["GH_ORG"], repository=env_vars["REPO"])
    approved_files = get_approved_files(repo)
    changed_files = env_vars["CHANGED_FILES"].split(",")
    block_pr = not check_files_in_approved_list(changed_files, approved_files)
    print(f"changed_files: {changed_files}")
    print(f"approved_files: {approved_files}")
    if block_pr:
        message = f"""Blocking PR because the changed files are not in the list of approved files.
                Update config at: {BOT_APPROVED_FILES_PATH} if necessary.
            """
        raise SystemExit(message)
    else:
        print("Changed files are in list of approved files.")


def main() -> None:
    env_vars = load_env_vars(REQUIRED_ENV_VARS)
    user = env_vars["USER"]

    # For now skip checks from dependabot until we decide how to handle them
    if user == "dependabot[bot]":
        print("Skipping checks for dependabot.")
        return

    check_if_pr_is_blocked(env_vars)


if __name__ == "__main__":
    main()
