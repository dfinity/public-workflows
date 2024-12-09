import os
from unittest import mock

import pytest

from shared.messages import (
    AGREED_MESSAGE,
    CLA_AGREEMENT_MESSAGE,
    FAILED_COMMENT,
    USER_AGREEMENT_MESSAGE,
)
from check_cla.check_cla_pr import CLAHandler, main


def test_init():
    gh = mock.Mock()
    cla_repo = mock.Mock()
    cla_repo.html_url = "repo_url"
    gh.repository.return_value = cla_repo

    cla = CLAHandler(gh)

    assert cla.cla_repo == cla_repo
    assert cla.cla_link == "repo_url/blob/main/CLA.md"
    gh.repository.assert_called_with(owner="dfinity", repository="cla")


def test_bot_comment_exists():
    cla = CLAHandler(mock.Mock())
    comments_iterator = mock.Mock()
    comment1 = mock.Mock()
    comment1.body = "comment1"
    comment2 = mock.Mock()
    comment2.body = "comment2"
    comments_iterator.__iter__ = mock.Mock(
        return_value=iter([comment1, comment2])
    )

    bot_comment = cla.check_if_comment_already_exists("comment1", comments_iterator)

    assert bot_comment is True


def test_no_bot_comment():
    cla = CLAHandler(mock.Mock())
    issue_comments = mock.Mock()
    comment1 = mock.Mock()
    comment1.body = "comment"
    issue_comments.__iter__ = mock.Mock(return_value=iter([comment1]))

    bot_comment = cla.check_if_comment_already_exists("comment2", issue_comments)

    assert bot_comment is False


def test_leave_failed_comment_on_issue():
    cla = CLAHandler(mock.Mock())
    issue = mock.Mock()
    issue.comments.return_value = mock.Mock()
    cla.check_if_comment_already_exists = mock.Mock(return_value=False)

    cla.leave_failed_comment_on_issue(issue)

    issue.create_comment.assert_called_once_with(FAILED_COMMENT)


def test_cla_is_signed(capfd):
    cla = CLAHandler(mock.Mock())
    issue = mock.Mock()
    comment = mock.Mock()
    comment.user.login = "username"
    agreement_message = USER_AGREEMENT_MESSAGE.format("username")
    comment.body = agreement_message
    issue.comments.return_value = [mock.Mock(), comment]

    response = cla.check_if_cla_signed(issue, "username")
    out, err = capfd.readouterr()

    assert response is True
    assert out == "CLA has been agreed to by username\n"


def test_cla_is_incorrectly_signed(capfd):
    cla = CLAHandler(mock.Mock())
    issue = mock.Mock()
    comment = mock.Mock()
    comment.user.login = "username"
    comment.body = "incorrect message"
    issue.comments.return_value = [mock.Mock(), comment]

    response = cla.check_if_cla_signed(issue, "username")
    out, err = capfd.readouterr()

    assert response is False
    assert out == "Comment created by username does not match CLA agreement.\nCLA is pending for username\n"  # fmt: skip


def test_cla_is_not_signed(capfd):
    cla = CLAHandler(mock.Mock())
    issue = mock.Mock()
    comment = mock.Mock()
    issue.comments.return_value = [mock.Mock(), comment]

    response = cla.check_if_cla_signed(issue, "username")
    out, err = capfd.readouterr()

    assert response is False
    assert out == "CLA is pending for username\n"


def test_get_cla_issue_success():
    cla = CLAHandler(mock.Mock())
    cla_repo = mock.Mock()
    issue = mock.Mock()
    issue.title = "cla: @username"
    cla_repo.issues.return_value = [mock.Mock(), issue]
    cla.cla_repo = cla_repo

    assert issue == cla.get_cla_issue("username")


def test_get_cla_issue_fails(capfd):
    cla = CLAHandler(mock.Mock())
    cla_repo = mock.Mock()
    issue = mock.Mock()
    issue.title = "cla: @another-username"
    cla_repo.issues.return_value = [mock.Mock(), issue]
    cla.cla_repo = cla_repo

    assert cla.get_cla_issue("username") is None
    out, err = capfd.readouterr()
    assert out == "No CLA issue for username\n"


def test_create_cla_issue():
    cla = CLAHandler(mock.Mock())
    cla_repo = mock.Mock()
    issue = mock.Mock()
    cla_repo.create_issue.return_value = issue
    cla.cla_repo = cla_repo
    cla.cla_link = "cla_repo_link"
    user_agreement_message = USER_AGREEMENT_MESSAGE.format("username")
    cla_agreement_message = CLA_AGREEMENT_MESSAGE.format(
        "username", cla.cla_link, user_agreement_message, "pr_url"
    )

    new_issue = cla.create_cla_issue("username", "pr_url")

    assert new_issue == issue
    cla_repo.create_issue.assert_called_with(
        "cla: @username",
        body=cla_agreement_message,
    )
    issue.add_labels.assert_called_with("cla:pending")


def test_handle_cla_signed_with_agreed_label():
    issue = mock.Mock()
    label = mock.Mock()
    label.name = "cla:agreed"
    issue.original_labels = [label]

    cla = CLAHandler(mock.Mock())
    cla.handle_cla_signed(issue, "username")

    issue.create_comment.assert_not_called()
    issue.remove_label.assert_not_called()


def test_handle_cla_signed_with_pending_label():
    issue = mock.Mock()
    label = mock.Mock()
    label.name = "cla:gh-wf-pending"
    issue.original_labels = [label]
    agreement_message = AGREED_MESSAGE.format("username")

    cla = CLAHandler(mock.Mock())
    cla.handle_cla_signed(issue, "username")

    issue.create_comment.assert_called_with(agreement_message)
    issue.remove_label.assert_called_once()
    issue.add_labels.assert_called_once()


def test_handle_cla_signed_with_new_pending_label():
    issue = mock.Mock()
    label = mock.Mock()
    label.name = "cla:pending"
    issue.original_labels = [label]
    agreement_message = AGREED_MESSAGE.format("username")

    cla = CLAHandler(mock.Mock())
    cla.handle_cla_signed(issue, "username")

    issue.create_comment.assert_called_with(agreement_message)
    issue.remove_label.assert_called_once()
    issue.add_labels.assert_called_once()


def test_handle_cla_signed_with_no_label(capfd):
    issue = mock.Mock()
    issue.original_labels = []

    with pytest.raises(SystemExit):
        cla = CLAHandler(mock.Mock())
        cla.handle_cla_signed(issue, "username")
        out, err = capfd.readouterr()
        assert out == "No cla labels found - manually check the cla issue to see what state it is in. Exiting program.\n"  # fmt: skip


@mock.patch.dict(
    os.environ,
    {"GH_ORG": "my_org", "GH_TOKEN": "secret", "REPO": "repo-name", "PR_ID": "1"},
)
@mock.patch("github3.login")
@mock.patch("check_cla.check_cla_pr.CLAHandler")
def test_end_to_end_env_vars_set(cla_mock, gh_login_mock):
    gh = mock.Mock()
    gh_login_mock.return_value = gh
    pr = mock.Mock()
    pr.user.login = "username"
    gh.pull_request.return_value = pr
    cla = mock.Mock()
    cla_mock.return_value = cla

    main()

    gh_login_mock.assert_called_with(token="secret")
    gh.pull_request.assert_called_with("my_org", "repo-name", "1")
    cla_mock.assert_called_with(gh)
    cla.get_cla_issue.assert_called_with("username")


@mock.patch.dict(
    os.environ,
    {"GH_ORG": "my_org", "GH_TOKEN": "secret", "REPO": "repo-name", "PR_ID": "1"},
)
@mock.patch("github3.login")
@mock.patch("check_cla.check_cla_pr.CLAHandler")
def test_end_to_end_no_issue(cla_mock, gh_login_mock):
    gh = mock.Mock()
    gh_login_mock.return_value = gh
    pr = mock.Mock()
    gh.pull_request.return_value = pr
    cla = mock.Mock()
    cla.get_cla_issue.return_value = None
    cla.check_if_cla_signed.return_value = False
    cla_mock.return_value = cla

    with pytest.raises(SystemExit):
        main()

    cla.create_cla_issue.assert_called_once()
    cla.comment_on_pr.assert_called_once()


@mock.patch.dict(
    os.environ,
    {"GH_ORG": "my_org", "GH_TOKEN": "secret", "REPO": "repo-name", "PR_ID": "1"},
)
@mock.patch("github3.login")
@mock.patch("check_cla.check_cla_pr.CLAHandler")
def test_end_to_end_cla_not_signed(cla_mock, gh_login_mock, capfd):
    gh = mock.Mock()
    gh_login_mock.return_value = gh
    pr = mock.Mock()
    gh.pull_request.return_value = pr
    cla = mock.Mock()
    issue = mock.Mock()
    issue.html_url = "url"
    cla.get_cla_issue.return_value = issue
    cla.check_if_cla_signed.return_value = False
    cla_mock.return_value = cla

    with pytest.raises(SystemExit):
        main()
        out, err = capfd.readouterr()
        assert out == "The CLA has not been signed. Please sign the CLA agreement: url"

    cla.create_cla_issue.assert_not_called()
    cla.check_if_cla_signed.assert_called_with(issue, pr.user.login)
    cla.comment_on_pr.assert_called_once()


@mock.patch.dict(
    os.environ,
    {"GH_ORG": "my_org", "GH_TOKEN": "secret", "REPO": "repo-name", "PR_ID": "1"},
)
@mock.patch("github3.login")
@mock.patch("check_cla.check_cla_pr.CLAHandler")
def test_end_to_end_cla_signed(cla_mock, gh_login_mock, capfd):
    gh = mock.Mock()
    gh_login_mock.return_value = gh
    pr = mock.Mock()
    pr.user.login = "username"
    gh.pull_request.return_value = pr
    cla = mock.Mock()
    issue = mock.Mock()
    cla.get_cla_issue.return_value = issue
    cla.check_if_cla_signed.return_value = True
    cla_mock.return_value = cla

    main()
    out, err = capfd.readouterr()

    assert out == "CLA has been signed.\n"
    cla.create_cla_issue.assert_not_called()
    cla.check_if_cla_signed.assert_called_with(issue, "username")
    cla.comment_on_pr.assert_not_called()


@mock.patch.dict(
    os.environ,
    {"GH_ORG": "my_org", "GH_TOKEN": "", "REPO": "repo-name", "PR_ID": "1"},
)
@mock.patch("github3.login")
def test_github_token_not_passed_in(github_login_mock):
    github_login_mock.return_value = None

    with pytest.raises(Exception) as exc:
        main()

    assert (
        str(exc.value) == "github login failed - maybe GH_TOKEN was not correctly set"
    )
