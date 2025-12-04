import os

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

def is_approved_bot(user: str) -> bool:
    """
    Return whether the user is an approved bot.
    """
    return user in APPROVED_BOT_LIST


def main() -> None:
    user = os.getenv("USER")

    is_bot = is_approved_bot(user)
    os.system(f"""echo 'is_bot={is_bot}' >> $GITHUB_OUTPUT""")

if __name__ == "__main__":
    main()
