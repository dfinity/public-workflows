import os

import github3

from check_membership.check_membership import is_approved_bot, is_member_of_org



def main() -> None:
    org = os.environ["GH_ORG"]
    gh_token = os.environ["GH_TOKEN"]
    user = os.environ["USER"]

    gh = github3.login(token=gh_token)

    if not gh:
        raise Exception("github login failed - maybe GH_TOKEN was not correctly set")

    is_member = is_member_of_org(gh, org, user)
    is_bot = is_approved_bot(user)

    org_member = is_member or is_bot

    if is_bot:
        print(f"{user} is an approved bot and can contribute.")
    if is_member:
        print(f"{user} is member of {org} and can contribute.")
    elif not org_member:
        print(f"{user} is an external contributor.")

    os.system(f"""echo 'is_member={org_member}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
