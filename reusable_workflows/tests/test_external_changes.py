import pytest
from unittest.mock import patch
from repo_policies.check_external_changes import check_files_against_blacklist



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
