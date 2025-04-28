from unittest import mock

import github3
import pytest

from repo_policies.check_bot_approved_files import (
    BOT_APPROVED_FILES_PATH,
    check_files_in_approved_list,
    check_if_pr_is_blocked,
    get_approved_files,
    get_approved_files_config,
)


@mock.patch("repo_policies.check_bot_approved_files.download_gh_file")
def test_get_approved_files_config(download_gh_file):
    repo = mock.Mock()
    config_file_mock = mock.Mock()
    download_gh_file.return_value = config_file_mock

    config_file = get_approved_files_config(repo)

    download_gh_file.assert_called_once_with(repo, BOT_APPROVED_FILES_PATH)
    assert config_file == config_file_mock


@mock.patch("repo_policies.check_bot_approved_files.download_gh_file")
def test_get_approved_files_config_fails(download_gh_file):
    repo = mock.Mock()
    download_gh_file.side_effect = github3.exceptions.NotFoundError(mock.Mock())

    with pytest.raises(Exception) as exc:
        get_approved_files_config(repo)

    assert (
        # fmt: off
        str(exc.value) == f"No config file found. Make sure you have a file saved at {BOT_APPROVED_FILES_PATH} in the default branch"
    )


@mock.patch("repo_policies.check_bot_approved_files.get_approved_files_config")
def test_get_approved_files(get_approved_files_config):
    config_file = open(
        "reusable_workflows/tests/test_data/BOT_APPROVED_FILES", "r"
    ).read()
    get_approved_files_config.return_value = config_file
    repo = mock.Mock()
    approved_files = get_approved_files(repo)

    assert approved_files == ["file1", "file2", "folder/*.txt"]


@mock.patch("repo_policies.check_bot_approved_files.get_approved_files_config")
def get_test_approved_files(get_approved_files_config):
    config_file = open(
        "reusable_workflows/tests/test_data/BOT_APPROVED_FILES", "r"
    ).read()
    get_approved_files_config.return_value = config_file
    repo = mock.Mock()
    approved_files = get_approved_files(repo)
    return approved_files


def test_check_files_in_approved_list_succeeds():
    changed_files = ["file1", "file2", "folder/file3.txt"]
    approved_files = get_test_approved_files()

    assert check_files_in_approved_list(changed_files, approved_files)

    changed_files = ["file1", "file2"]

    assert check_files_in_approved_list(changed_files, approved_files)

    changed_files = ["file1", "file2", "folder/subfolder/file3.txt"]
    approved_files = get_test_approved_files()

    assert check_files_in_approved_list(changed_files, approved_files)

def test_check_files_in_approved_list_fails():
    changed_files = ["file1", "file2", "folder/file3.txt", 'folder/file4.py']
    approved_files = get_test_approved_files()

    assert not check_files_in_approved_list(changed_files, approved_files)


@mock.patch("repo_policies.check_bot_approved_files.get_approved_files")
@mock.patch("github3.login")
def test_pr_is_blocked_false(gh_login, get_approved_files):
    env_vars = {
        "CHANGED_FILES": "file1,file2",
        "GH_TOKEN": "token",
        "GH_ORG": "org",
        "REPO": "repo",
    }
    gh = mock.Mock()
    gh_login.return_value = gh
    approved_files = get_test_approved_files()
    get_approved_files.return_value = approved_files

    check_if_pr_is_blocked(env_vars)


@mock.patch("repo_policies.check_bot_approved_files.get_approved_files")
@mock.patch("github3.login")
def test_pr_is_blocked_true(gh_login, get_approved_files):
    env_vars = {
        "CHANGED_FILES": "file1,file2,file3",
        "GH_TOKEN": "token",
        "GH_ORG": "org",
        "REPO": "repo",
    }
    gh = mock.Mock()
    gh_login.return_value = gh
    approved_files = get_test_approved_files()
    get_approved_files.return_value = approved_files

    with pytest.raises(SystemExit):
        check_if_pr_is_blocked(env_vars)
