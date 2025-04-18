import pytest
import subprocess
from unittest.mock import patch
from repo_policies.check_external_changes import get_changed_files, check_files_against_blacklist


@patch("subprocess.run")
def test_get_changed_files(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=["git", "diff", "--name-only", "HEAD..branch"],
        returncode=0,
        stdout="file1.py\nfile2.md\n"
    )

    changed_files = get_changed_files("HEAD", "branch","repo-path")
    assert changed_files == ["file1.py", "file2.md"]


@patch("subprocess.run")
def test_get_changed_files_empty(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=["git", "diff", "--name-only", "HEAD..branch"],
        returncode=0,
        stdout=""
    )

    changed_files = get_changed_files("HEAD", "branch", "repo-path")
    assert changed_files == []


@patch("os.system")
def test_check_files_against_blacklist_match(os_system):
    changed_files = ["file1.py", "docs/README.md"]
    blacklist_files = ["file2.*", "docs/*.md"]

    with pytest.raises(SystemExit):
        check_files_against_blacklist(changed_files, blacklist_files)


def test_check_files_against_blacklist_no_match():
    changed_files = ["file1.txt", "docs/README.txt"]
    blacklist_files = ["*.py", "docs/*.md"]

    # Should not raise an exception
    check_files_against_blacklist(changed_files, blacklist_files)


def test_check_files_against_blacklist_empty_blacklist():
    changed_files = ["file1.py", "docs/README.md"]
    blacklist_files = []

    # Should not raise an exception
    check_files_against_blacklist(changed_files, blacklist_files)
