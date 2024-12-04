import os
import time

import github3


def download_gh_file(repo: github3.github.repo, file_path: str) -> str:
    # sometimes the request does not work the first time, so set a retry
    for attempt in range(5):
        try:
            file_content = repo.file_contents(file_path)
            break
        except ConnectionResetError as error:
            if attempt < 4:
                time.sleep(pow(2, attempt))
                print(f"Retrying file download, waiting {pow(2, attempt)} seconds.")
                continue
            else:
                # if it hasn't succeeded after 5 tries, raise the error
                raise Exception(
                    "Error downloading data. Try rerunning the CI job"
                ) from error

    file_decoded = file_content.decoded.decode()
    return file_decoded


def load_env_vars(var_names: list[str]) -> dict:
    env_vars = {}
    for var in var_names:
        try:
            env_vars[var] = os.environ[var]
        except KeyError:
            raise Exception(f"Environment variable '{var}' is not set.")
    return env_vars
