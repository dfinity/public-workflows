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


def test_get_approved_files():
    config_file = open(
        "reusable_workflows/tests/test_data/BOT_APPROVED_FILES", "r"
    ).read()
    approved_files = get_approved_files(config_file)

    assert approved_files == ["file1", "file2", "folder/*.txt"]


def get_test_approved_files():
    config_file = open(
        "reusable_workflows/tests/test_data/BOT_APPROVED_FILES", "r"
    ).read()
    approved_files = get_approved_files(config_file)
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


@mock.patch("repo_policies.check_bot_approved_files.get_changed_files")
@mock.patch(
    "repo_policies.check_bot_approved_files.get_approved_files_config"
)
@mock.patch("github3.login")
def test_pr_is_blocked_false(gh_login, get_approved_files_config, get_changed_files):
    env_vars = {
        "GH_TOKEN": "token",
        "GH_ORG": "org",
        "REPO": "repo",
        "REPO_PATH": "path",
        "MERGE_BASE_SHA": "base",
        "BRANCH_HEAD_SHA": "head",
    }
    gh = mock.Mock()
    gh_login.return_value = gh
    repo = mock.Mock()
    gh.repository.return_value = repo
    get_changed_files.return_value = ["file1", "file2"]
    config_file = open(
        "reusable_workflows/tests/test_data/BOT_APPROVED_FILES", "r"
    ).read()
    get_approved_files_config.return_value = config_file

    check_if_pr_is_blocked(env_vars)

    get_changed_files.assert_called_once_with("base", "head", "path")
    get_approved_files_config.assert_called_once_with(repo)


@mock.patch("repo_policies.check_bot_approved_files.get_changed_files")
@mock.patch(
    "repo_policies.check_bot_approved_files.get_approved_files_config"
)
@mock.patch("github3.login")
def test_pr_is_blocked_true(gh_login, get_approved_files_config, get_changed_files):
    env_vars = {
        "GH_TOKEN": "token",
        "GH_ORG": "org",
        "REPO": "repo",
        "REPO_PATH": "path",
        "MERGE_BASE_SHA": "base",
        "BRANCH_HEAD_SHA": "head",
    }
    gh = mock.Mock()
    gh_login.return_value = gh
    repo = mock.Mock()
    gh.repository.return_value = repo
    get_changed_files.return_value = ["file1", "file2", "file3"]
    config_file = open(
        "reusable_workflows/tests/test_data/BOT_APPROVED_FILES", "r"
    ).read()
    get_approved_files_config.return_value = config_file

    with pytest.raises(SystemExit):
        check_if_pr_is_blocked(env_vars)

    get_changed_files.assert_called_once_with("base", "head", "path")
    get_approved_files_config.assert_called_once_with(repo)
