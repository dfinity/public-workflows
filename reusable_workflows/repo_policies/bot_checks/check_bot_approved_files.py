import json
import subprocess

import github3

from check_membership.check_membership import is_approved_bot
from shared.utils import download_gh_file, load_env_vars

BOT_APPROVED_FILES_PATH = ".github/repo_policies/bot_approved_files.json"
REQUIRED_ENV_VARS = [
    "USER",
    "GH_TOKEN",
    "GH_ORG",
    "REPO",
    "MERGE_BASE_SHA",
    "BRANCH_HEAD_SHA",
]


def get_changed_files(merge_base_sha: str, branch_head_sha: str) -> list[str]:
    """
    Compares the files changed in the current branch to the merge base.
    """
    commit_range = f"{merge_base_sha}..{branch_head_sha}"
    result = subprocess.run(
        ["git", "diff", "--name-only", commit_range], stdout=subprocess.PIPE, text=True
    )
    changed_files = result.stdout.strip().split("\n")
    return changed_files


def get_approved_files_config(repo: github3.github.repo) -> str:
    """
    Loads the config from the repository that contains the list of approved files.
    """
    try:
        config_file = download_gh_file(repo, BOT_APPROVED_FILES_PATH)
        return config_file
    except github3.exceptions.NotFoundError:
        raise Exception(
            f"No config file found. Make sure you have a file saved at {BOT_APPROVED_FILES_PATH}"
        )


def get_approved_files(config_file: str) -> list[str]:
    """
    Extracts the list of approved files from the config file.
    """
    try:
        config = json.loads(config_file)
    except json.JSONDecodeError:
        raise Exception("Config file is not a valid JSON file")
    try:
        approved_files = config["approved_files"]
    except KeyError:
        raise Exception("No approved_files key found in config file")

    if len(approved_files) == 0:
        raise Exception("No approved files found in config file")
    return approved_files


def pr_is_blocked(env_vars: dict) -> bool:
    """
    Logic to check if the Bot's PR can be merged or should be blocked.
    """
    gh = github3.login(token=env_vars["GH_TOKEN"])
    repo = gh.repository(owner=env_vars["GH_ORG"], repository=env_vars["REPO"])
    changed_files = get_changed_files(
        env_vars["MERGE_BASE_SHA"], env_vars["BRANCH_HEAD_SHA"]
    )
    config = get_approved_files_config(repo)
    approved_files = get_approved_files(config)
    block_pr = not all(file in approved_files for file in changed_files)
    if block_pr:
        print(
            f"""Blocking PR because the changed files are not in the list of approved files.
                Update config at: {BOT_APPROVED_FILES_PATH} if necessary.
            """
        )

    return block_pr


def main() -> None:
    env_vars = load_env_vars(REQUIRED_ENV_VARS)
    user = env_vars["USER"]

    is_bot = is_approved_bot(user)

    if is_bot:
        block_pr = pr_is_blocked(env_vars)

    else:
        print(
            f"{user} is not a bot. Letting CLA check handle contribution decision."
        )
        block_pr = False

    subprocess.run(f"""echo 'block_pr={block_pr}' >> $GITHUB_OUTPUT""", shell=True)


if __name__ == "__main__":
    main()
