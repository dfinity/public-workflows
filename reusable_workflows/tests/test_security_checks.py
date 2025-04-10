import pytest
import subprocess
from unittest.mock import patch, mock_open
from security_checks.security_checks import get_changed_files, load_config, check_files_against_blacklist


@patch("subprocess.run")
def test_get_changed_files(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=["git", "diff", "--name-only", "HEAD..branch"],
        returncode=0,
        stdout="file1.py\nfile2.md\n"
    )

    changed_files = get_changed_files("HEAD", "branch")
    assert changed_files == ["file1.py", "file2.md"]


@patch("subprocess.run")
def test_get_changed_files_empty(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=["git", "diff", "--name-only", "HEAD..branch"],
        returncode=0,
        stdout=""
    )

    changed_files = get_changed_files("HEAD", "branch")
    assert changed_files == []


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='{"repo1": ["*.py", "docs/*.md"]}')
def test_load_config(mock_open_file, mock_path_exists):
    config = load_config(".github/workflows/config.json", "repo1")
    assert config == ["*.py", "docs/*.md"]

def test_load_real_config():
    config = load_config(".github/workflows/config.json", "public-workflows")
    assert config == [".github/*"]

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='{"repo1": ["*.py", "docs/*.md"]}')
def test_load_config_empty(mock_open_file, mock_path_exists):
    config = load_config(".github/workflows/config.json", "repo2")
    assert config == []


@patch("os.path.exists", return_value=False)
def test_load_config_file_not_found(mock_path_exists):
    with pytest.raises(SystemExit) as excinfo:
        load_config(".github/workflows/config.json", "repo1")
    assert excinfo.value.code == 1


@patch("builtins.open", new_callable=mock_open, read_data='invalid json')
@patch("os.path.exists", return_value=True)
def test_load_config_invalid_json(mock_path_exists, mock_open_file):
    with pytest.raises(SystemExit) as excinfo:
        load_config(".github/workflows/config.json", "repo1")
    assert excinfo.value.code == 1


@patch("os.system")
def test_check_files_against_blacklist_match(os_system):
    changed_files = ["file1.py", "docs/README.md"]
    blacklist_files = ["file2.*", "docs/*.md"]

    with pytest.raises(SystemExit) as excinfo:
        check_files_against_blacklist(changed_files, blacklist_files)
    os_system.assert_called_once_with("echo 'close_pr=true' >> $GITHUB_OUTPUT")


@patch("os.system")
def test_check_files_against_blacklist_no_match(os_system):
    changed_files = ["file1.txt", "docs/README.txt"]
    blacklist_files = ["*.py", "docs/*.md"]

    # Should not raise an exception
    check_files_against_blacklist(changed_files, blacklist_files)
    os_system.assert_called_once_with("echo 'close_pr=false' >> $GITHUB_OUTPUT")



@patch("os.system")
def test_check_files_against_blacklist_empty_blacklist(os_system):
    changed_files = ["file1.py", "docs/README.md"]
    blacklist_files = []

    # Should not raise an exception
    check_files_against_blacklist(changed_files, blacklist_files)
    os_system.assert_called_once_with("echo 'close_pr=false' >> $GITHUB_OUTPUT")
