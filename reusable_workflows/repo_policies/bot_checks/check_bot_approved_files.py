import os

from check_membership.check_membership import is_approved_bot



def main() -> None:

    user = os.environ["USER"]
    changed_files = os.environ["CHANGED_FILES"]
    approved_files = os.environ["APPROVED_FILES"]
    is_bot = is_approved_bot(user)
    
    if is_bot:
        check_changed_files = 

    else:
        print(f"{user} is not an approved bot. Letting CLA check handle contribution decision.")
        block_pr = False

    os.system(f"""echo 'block_pr={block_pr}' >> $GITHUB_OUTPUT""")


if __name__ == "__main__":
    main()
