# Messages
CLOSING_MESSAGE = """Dear @{},

Thank you for contributing! Unfortunately this repository does not accept external contributions yet.

We are working on enabling this by aligning our internal processes and our CI setup to handle external contributions. However this will take some time to set up so in the meantime we unfortunately have to close this Pull Request.

We hope you understand and will come back once we accept external PRs.

— The DFINITY Foundation"""

USER_AGREEMENT_MESSAGE = "I, {}, hereby agree to the DFINITY Foundation's CLA."

CLA_MESSAGE = """Dear @{},

In order to potentially merge your code in this open-source repository and therefore proceed with your contribution, we need to have your approval on DFINITY's [CLA]({}).

If you decide to agree with it, please visit this [issue]({}) and read the instructions there. Once you have signed it, re-trigger the workflow on this PR to see if your code can be merged.

— The DFINITY Foundation"""

CLA_AGREEMENT_MESSAGE = """Dear @{},

In order to potentially merge your code in this open-source repository and therefore proceed with your contribution, we need to have your approval on the following [CLA]({}).

If you decide to agree with it, please reply with the following message:
> {}

— The DFINITY Foundation"""

AGREED_MESSAGE = """Dear @{},

As you have agreed to the CLA, I added the `cla:agreed` label to your PR and we are now able to proceed with your contribution."""

FAILED_COMMENT = """Your comment does not match the CLA agreement.

Check that the sentence has been copied exactly, including punctuation and does not contain any other text."""
