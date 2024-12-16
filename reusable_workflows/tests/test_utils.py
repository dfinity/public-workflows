import os
from unittest import mock

import pytest

from shared.utils import download_gh_file, load_env_vars


def test_download_file_succeeds_first_try():
    repo = mock.MagicMock()
    file_content_obj = mock.Mock()
    file_content_obj.decoded = b"file_contents"
    repo.file_contents.return_value = file_content_obj

    data = download_gh_file(repo, "file_path")

    assert data == "file_contents"
    repo.file_contents.assert_called_with("file_path")
    assert repo.file_contents.call_count == 1


@pytest.mark.integration
def test_download_file_succeeds_third_try():
    repo = mock.MagicMock()
    file_content_obj = mock.Mock()
    file_content_obj.decoded = b"file_contents"
    repo.file_contents = mock.Mock(
        side_effect=[ConnectionResetError, ConnectionResetError, file_content_obj]
    )

    data = download_gh_file(repo, "file_path")

    assert data == "file_contents"
    repo.file_contents.assert_called_with("file_path")
    assert repo.file_contents.call_count == 3


@pytest.mark.integration
@mock.patch("requests.get")
def test_download_file_fails(mock_get):
    repo = mock.MagicMock()
    file_content_obj = mock.Mock()
    repo.file_contents = mock.Mock(side_effect=ConnectionResetError)

    with pytest.raises((ConnectionResetError, Exception)):
        download_gh_file(repo, "file_path")

    assert repo.file_contents.call_count == 5
    file_content_obj.decoded.assert_not_called


@mock.patch.dict(os.environ, {"REPO": "repo-1", "GH_TOKEN": "token"})
def test_load_env_vars_succeeds(capfd):
    env_vars = load_env_vars(["REPO", "GH_TOKEN"])

    assert env_vars == {"REPO": "repo-1", "GH_TOKEN": "token"}


@mock.patch.dict(os.environ, {"REPO": "repo-1"}, clear=True)
def test_load_env_vars_fails(capfd):
    with pytest.raises(Exception) as exc:
        env_vars = load_env_vars(["REPO", "GH_TOKEN"])
        print(env_vars)
    assert str(exc.value) == "Environment variable 'GH_TOKEN' is not set."
