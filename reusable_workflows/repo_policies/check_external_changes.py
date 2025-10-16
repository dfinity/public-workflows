#!/usr/bin/env python3
import fnmatch
import os
import sys
from pathlib import Path


def main():
    changed_files = Path(os.environ['CHANGED_FILES_PATH']).read_text().splitlines()

    EXTERNAL_CONTRIB_BLACKLIST_PATH = os.environ['EXTERNAL_CONTRIB_BLACKLIST_PATH']
    if not (os.path.exists(EXTERNAL_CONTRIB_BLACKLIST_PATH)):
        print(f"Blacklist file {EXTERNAL_CONTRIB_BLACKLIST_PATH} not found, skipping checks.")
        sys.exit(0)

    blacklist_files = [
        pattern for pattern in Path(EXTERNAL_CONTRIB_BLACKLIST_PATH).read_text().splitlines()
        if not (pattern == "" or pattern.startswith("#"))
    ]
    print(f"Changed files: {changed_files}")
    print(f"Blacklisted patterns: {blacklist_files}")

    if blacklist_files == []:
        print("No blacklisted files found.")
        sys.exit(0)

    violations = []
    for file in changed_files:
        for pattern in blacklist_files:
            if fnmatch.fnmatch(file, pattern):  # Use glob pattern matching
                violations.append(file)

    if len(violations) > 0:
        print(f"No changes allowed to files: {violations}")
        sys.exit(1)

    print("All changed files pass conditions.")


if __name__ == "__main__":
    main()