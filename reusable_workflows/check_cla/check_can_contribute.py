import os
from typing import List

import github3

from shared.utils import download_gh_file

APPROVED_CONTRIBUTOR_LIST = ["droid-uexternal"]


def get_repos_open_to_contributions(gh: github3.login) -> List[str]:
    org = "dfinity"
    repo_name = "repositories-open-to-contributions"
    file_path = "open-repositories.txt"

    repo = gh.repository(owner=org, repository=repo_name)

    file_content = download_gh_file(repo, file_path)

    # convert .txt file to list and strip out comments
    repo_list = [line.split("#")[0].strip() for line in file_content.split("\n") if line.split("#")[0].strip()]
    return repo_list


def main() -> None:
    repo = os.environ["REPO"]
    user = os.environ["USER"]
    gh_token = os.environ["GH_TOKEN"]

    gh = github3.login(token=gh_token)

    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    repo_list = get_repos_open_to_contributions(gh)
    repo_accepts_contributions = repo in repo_list
    user_is_approved_contributor = user in APPROVED_CONTRIBUTOR_LIST
    
    can_contribute = repo_accepts_contributions or user_is_approved_contributor

    os.system(f"""echo 'can_contribute={can_contribute}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
