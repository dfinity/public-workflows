#!/usr/bin/env python3
import fnmatch
import json
import os
import sys
from pathlib import Path


def main():
    EXTERNAL_CONTRIB_BLACKLIST_PATH = os.environ['EXTERNAL_CONTRIB_BLACKLIST_PATH']

    blacklisted_patterns = [
        pattern for line in Path(EXTERNAL_CONTRIB_BLACKLIST_PATH).read_text().splitlines()
        if (pattern := line.split("#")[0].strip()) != ""
    ]

    with open(os.environ['CHANGED_FILES_JSON_PATH'], 'r') as f:
        changed_files = json.load(f)

    print(f"Changed files: {changed_files}")
    print(f"Blacklisted patterns: {blacklisted_patterns}")

    if blacklisted_patterns == []:
        print("No blacklisted patterns found.")
        sys.exit(0)

    violations = [
        file for pattern in blacklisted_patterns for file in changed_files
        if fnmatch.fnmatch(file, pattern)
    ]

    if len(violations) > 0:
        print(f"No changes allowed to files: {violations}")
        sys.exit(1)

    print("All changed files pass conditions.")


if __name__ == "__main__":
    main()