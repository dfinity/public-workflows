import json
import os
import subprocess

import github3

from check_membership.check_membership import is_approved_bot


def get_changed_files() -> list[str]:
    merge_base_sha = os.environ["MERGE_BASE_SHA"]
    branch_head_sha = os.environ["BRANCH_HEAD_SHA"]

    commit_range = f"{merge_base_sha}..{branch_head_sha}"
    result = subprocess.run(['git', 'diff', '--name-only', commit_range], stdout=subprocess.PIPE, text=True)
    changed_files = result.stdout.strip().split('\n')
    return changed_files

def get_approved_files_config(repo: github3.github.repo) -> str:
    bot_approved_files_list = [
        ".github/repo_policies/bot_approved_files.json",
    ]
    for path in bot_approved_files_list:
        try:
            config_file = repo.file_contents(path)
            return config_file
        except github3.exceptions.NotFoundError:
            print("No config file found")
            raise Exception("No config file found")

def get_approved_files(config_file: str) -> list[str]:
    with open(config_file, 'r') as f:
        data = json.load(f)
    try:
        approved_files = data["approved_files"]
    except KeyError:
        raise Exception("No approved_files key found in config file")
    
    if len(approved_files) == 0:
        print("No approved files found in config file")
        raise Exception("No approved files found in config file")
    return approved_files 

def main() -> None:

    gh_token = os.environ["GH_TOKEN"]
    org_name = os.environ["GH_ORG"]
    repo_name = os.environ["REPO"]
    user = os.environ["USER"]
    is_bot = is_approved_bot(user)
    
    if is_bot:
        gh = github3.login(token=gh_token)
        repo = gh.repository(owner=org_name, repository=repo_name)
        changed_files = get_changed_files()
        config = get_approved_files_config(repo)
        approved_files = get_approved_files(config)
        block_pr = not all(file in approved_files for file in changed_files)

    else:
        print(f"{user} is not an approved bot. Letting CLA check handle contribution decision.")
        block_pr = False

    os.system(f"""echo 'block_pr={block_pr}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
