import os

from check_membership.check_membership import is_approved_bot


def main() -> None:
    user = os.getenv("USER")

    is_bot = is_approved_bot(user)
    os.system(f"""echo 'is_bot={is_bot}' >> $GITHUB_OUTPUT""")
