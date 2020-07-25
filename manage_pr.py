#!/usr/bin/env python3

import os
import logging
import argparse
from github import Github

logger = None

MAGIC_LINE = "BlueZ Testbot Message:"

PATCH_SUBMISSION_MSG = '''
This is an automated message and please do not change or delete.

Dear submitter,

Thanks for submitting the pull request to the BlueZ github repo.
Currently, the BlueZ repo in Github is only for CI and testing purposes,
and not accepting any pull request at this moment.

If you still want us to review your patch and merge them, please send your
patch to the Linux Bluetooth mailing list(linux-bluetooth@vger.kernel.org).

For more detail about submitting a patch to the mailing list,
Please refer \"Submitting patches\" section in the HACKING file in the source.

Note that this pull request will be closed in the near future.

Best regards,
BlueZ Team
'''

def init_logging():
    """
    Initialize the logger and set the level to DEBUG
    """

    global logger

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s:%(levelname)-8s:%(message)s')
    sh.setFormatter(formatter)

    logger.addHandler(sh)

    logger.info("Logger is initialized")

def add_comment_patch_submission(pr):
    """
    Add patch submission message to comment
    """
    # Start the message with MAGIC_LINE so it can be searched later
    comment = MAGIC_LINE + "\n\n" + PATCH_SUBMISSION_MSG
    pr.create_issue_comment(comment)

def notify_patch_submission(pr):
    """
    Notify the submitter about patch submission via mailing list in
    comment
    """

    new_pr = True

    pr_comments = pr.get_issue_comments()
    logger.info("PR#%s Comment count: %s" % (pr.number, pr_comments.totalCount))

    if (pr_comments.totalCount == 0):
        # Empty comment and add message
        add_comment_patch_submission(pr)
        return

    # Check if the pr was already handled
    for comment in pr_comments:
        body = comment.body

        if (body.find(MAGIC_LINE) != -1):
            logger.debug("Found MAGIC_LINE")
            new_pr = False
            break

    if (new_pr):
        logger.debug("PR#%s is new PR and add message" % pr.number)
        add_comment_patch_submission(pr)

def manage_pr(github_repo):
    """
    Manage PR
    """

    pr_list = github_repo.get_pulls(state="open")

    logger.info("Pull Request count: %s(open)" % pr_list.totalCount)

    # Handle each PR
    for pr in pr_list:
        # Notify about patch submission via mailing list in comments
        notify_patch_submission(pr)


def parse_args():
    """ Parse input argument """

    ap = argparse.ArgumentParser(
        description="Manage PR"
    )

    ap.add_argument("-r", "--repo", required=True,
                    help="The name of target repo to mange PR")

    return ap.parse_args()

def main():
    args = parse_args()

    init_logging()

    # Initialize github repo object
    github_repo = Github(os.environ['ACTION_TOKEN']).get_repo(args.repo)

    manage_pr(github_repo)

if __name__ == "__main__":
    main()

