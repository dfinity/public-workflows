import fnmatch
import sys
from pathlib import Path


def main():
    changed_files = Path(".github/outputs/added_files.txt").read_text().splitlines()
    blacklist_files = Path("repo/.github/repo_policies/EXTERNAL_CONTRIB_BLACKLIST").read_text().splitlines()

    if blacklist_files == []:
        print("No blacklisted files found.")
        sys.exit(0)

    violations = []
    for file in changed_files:
        for rule in blacklist_files:
            print("Checking file", file, "against rule", rule)
            if fnmatch.fnmatch(file, rule):  # Use glob pattern matching
                violations.append(file)

    if len(violations) > 0:
        print(f"No changes allowed to files: {violations}")
        sys.exit(1)

    print("All changed files pass conditions.")


if __name__ == "__main__":
    main()