#!/usr/bin/env python3
import fnmatch
import os
import sys
from pathlib import Path


def main():
    changed_files = Path(os.environ['CHANGED_FILES_PATH']).read_text().splitlines()
    blacklist_files = [
        pattern for pattern in Path(os.environ['EXTERNAL_CONTRIB_BLACKLIST_PATH']).read_text().splitlines()
        if not(pattern == "" or pattern.startswith("#"))
    ]

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