import os
from typing import List

import github3

from shared.utils import download_gh_file


def get_repos_open_to_contributions(gh: github3.login) -> List[str]:
    org = "dfinity"
    repo_name = "repositories-open-to-contributions"
    file_path = "open-repositories.txt"

    repo = gh.repository(owner=org, repository=repo_name)

    file_content = download_gh_file(repo, file_path)

    # convert .txt file to list and strip out comments
    repo_list = [line.strip() for line in file_content.split("\n") if line.strip() and not line.strip().startswith("#")]
    return repo_list


def main() -> None:
    repo = os.environ["REPO"]
    gh_token = os.environ["GH_TOKEN"]

    gh = github3.login(token=gh_token)

    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    repo_list = get_repos_open_to_contributions(gh)
    accepts_contrib = repo in repo_list

    os.system(f"""echo 'accepts_contrib={accepts_contrib}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
