import os

import github3


APPROVED_BOT_LIST = [
    "dependabot[bot]",
    "dfinity-bot",
    "github-actions[bot]",
    "gix-bot",
    "mergify[bot]",
    "pr-automation-bot-public[bot]",
    "pr-creation-bot-dfinity-ic[bot]",
    "pr-creation-bot-dfinity[bot]",
    "sa-github-api",
]

APPROVED_EXTERNAL_CONTRIBUTORS = [
    "droid-uexternal"
]

def is_approved_bot(user: str) -> bool:
    """
    Return whether the user is an approved bot.
    """
    return user in APPROVED_BOT_LIST

def is_approved_external_contributor(user: str) -> bool:
    """
    Return whether the user is an approved external contributor.
    """
    return user in APPROVED_EXTERNAL_CONTRIBUTORS


def is_member_of_org(gh: github3.login, org: str, user: str) -> bool:
    """
    Return whether the user is a member of the organisation.
    """
    return gh.organization(org).is_member(user)


def is_approved_member(gh: github3.login, org: str, user: str):
    if is_member_of_org(gh, org, user):
        print(f"{user} is member of {org} and can contribute.")
        return True
    elif is_approved_bot(user):
        print(f"{user} is an approved bot and can contribute.")
        return True
    elif is_approved_external_contributor(user):
        print(f"{user} is an approved external contributor and can contribute.")
        return True
    else:
        print(f"{user} is an external contributor.")
        return False


def main() -> None:
    org = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    user = os.environ["USER"]

    gh = github3.login(token=gh_token)

    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    org_member = is_approved_member(gh, org, user)

    os.system(f"""echo 'is_member={org_member}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
