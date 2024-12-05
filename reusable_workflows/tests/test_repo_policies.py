import subprocess
from unittest import mock

import github3
import pytest

from repo_policies.bot_checks.check_bot_approved_files import (
    BOT_APPROVED_FILES_PATH,
    get_approved_files,
    get_approved_files_config,
    get_changed_files,
    main,
    pr_is_blocked,
)


@mock.patch("subprocess.run")
def test_get_changed_files(mock_subprocess_run):
    mock_subprocess_run.return_value = mock.Mock(stdout="file1.py\nfile2.py\n")

    changed_files = get_changed_files("merge_base_sha", "branch_head_sha")

    assert changed_files == ["file1.py", "file2.py"]
    mock_subprocess_run.assert_called_once_with(
        ["git", "diff", "--name-only", "merge_base_sha..branch_head_sha"],
        stdout=subprocess.PIPE,
        text=True,
    )


@mock.patch("repo_policies.bot_checks.check_bot_approved_files.download_gh_file")
def test_get_approved_files_config(download_gh_file):
    repo = mock.Mock()
    config_file_mock = mock.Mock()
    download_gh_file.return_value = config_file_mock

    config_file = get_approved_files_config(repo)

    download_gh_file.assert_called_once_with(repo, BOT_APPROVED_FILES_PATH)
    assert config_file == config_file_mock


@mock.patch("repo_policies.bot_checks.check_bot_approved_files.download_gh_file")
def test_get_approved_files_config_fails(download_gh_file):
    repo = mock.Mock()
    download_gh_file.side_effect = github3.exceptions.NotFoundError(mock.Mock())

    with pytest.raises(Exception) as exc:
        get_approved_files_config(repo)

    assert (
        # fmt: off
        str(exc.value) == f"No config file found. Make sure you have a file saved at {BOT_APPROVED_FILES_PATH}"
    )


def test_get_approved_files():
    config_file = open(
        "reusable_workflows/tests/test_data/BOT_APPROVED_FILES", "r"
    ).read()
    approved_files = get_approved_files(config_file)

    assert approved_files == ["file1", "file2"]


def test_get_approved_files_empty():
    config_file = ""

    with pytest.raises(ValueError) as exc:
        get_approved_files(config_file)

    assert str(exc.value) == "No approved files found in config file"


@mock.patch("repo_policies.bot_checks.check_bot_approved_files.get_changed_files")
@mock.patch(
    "repo_policies.bot_checks.check_bot_approved_files.get_approved_files_config"
)
@mock.patch("github3.login")
def test_pr_is_blocked_false(gh_login, get_approved_files_config, get_changed_files):
    env_vars = {
        "GH_TOKEN": "token",
        "GH_ORG": "org",
        "REPO": "repo",
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

    blocked = pr_is_blocked(env_vars)

    assert blocked is False
    get_changed_files.assert_called_once_with("base", "head")
    get_approved_files_config.assert_called_once_with(repo)


@mock.patch("repo_policies.bot_checks.check_bot_approved_files.get_changed_files")
@mock.patch(
    "repo_policies.bot_checks.check_bot_approved_files.get_approved_files_config"
)
@mock.patch("github3.login")
def test_pr_is_blocked_true(gh_login, get_approved_files_config, get_changed_files):
    env_vars = {
        "GH_TOKEN": "token",
        "GH_ORG": "org",
        "REPO": "repo",
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

    blocked = pr_is_blocked(env_vars)

    assert blocked is True
    get_changed_files.assert_called_once_with("base", "head")
    get_approved_files_config.assert_called_once_with(repo)


@mock.patch("repo_policies.bot_checks.check_bot_approved_files.load_env_vars")
@mock.patch("repo_policies.bot_checks.check_bot_approved_files.is_approved_bot")
@mock.patch("repo_policies.bot_checks.check_bot_approved_files.pr_is_blocked")
@mock.patch("subprocess.run")
def test_main_succeeds(subprocess_run, pr_is_blocked, is_approved_bot, load_env_vars):
    env_vars = {"GH_TOKEN": "token", "USER": "user"}
    load_env_vars.return_value = env_vars
    is_approved_bot.return_value = True
    pr_is_blocked.return_value = False

    main()

    subprocess_run.assert_called_once_with(
        "echo 'block_pr=False' >> $GITHUB_OUTPUT", shell=True
    )


@mock.patch("repo_policies.bot_checks.check_bot_approved_files.load_env_vars")
@mock.patch("repo_policies.bot_checks.check_bot_approved_files.is_approved_bot")
@mock.patch("repo_policies.bot_checks.check_bot_approved_files.pr_is_blocked")
@mock.patch("subprocess.run")
def test_main_not_a_bot(subprocess_run, pr_is_blocked, is_approved_bot, load_env_vars):
    env_vars = {"GH_TOKEN": "token", "USER": "user"}
    load_env_vars.return_value = env_vars
    is_approved_bot.return_value = False

    main()

    subprocess_run.assert_called_once_with(
        "echo 'block_pr=False' >> $GITHUB_OUTPUT", shell=True
    )
    pr_is_blocked.assert_not_called()
