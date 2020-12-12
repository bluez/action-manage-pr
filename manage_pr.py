#!/usr/bin/env python3

import os
import logging
import argparse
from datetime import datetime
from github import Github

logger = None

MAGIC_LINE = "BlueZ Testbot Message:"
MAGIC_LINE_2 = "BlueZ Testbot Message #2:"
MAGIC_LINE_3 = "BlueZ Testbot Message #3:"
MAGIC_LINE_4 = "BlueZ Testbot Message #4:"

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

PATCH_SUBMISSION_MSG_2 = '''
This is an automated message and please do not change or delete.

Dear submitter,

This is a friendly reminder that this pull request will be closed within
a week or two.

If you already submitted the patches to the Linux Bluetooth mailing list
(linux-bluetooth@vger.kernel.org) for review, Please close this pull
request.

If you haven't submitted the patches but still want us to review your patch,
please send your patch to the Linux Bluetooth mailing list
(linux-bluetooth@vger.kernel.org).

For more detail about submitting a patch to the mailing list,
Please refer \"Submitting patches\" section in the HACKING file in the source.

Note that this pull request will be closed in a week or two.

Best regards,
BlueZ Team
'''

PATCH_SUBMISSION_MSG_3 = '''
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

PATCH_SUBMISSION_MSG_4 = '''
This is an automated message and please do not change or delete.

Closing without taking any action.

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

def get_comment_str(magic_line):
    """
    Generate the comment string including magic_line
    """
    if magic_line == MAGIC_LINE:
        msg = PATCH_SUBMISSION_MSG
    if magic_line == MAGIC_LINE_2:
        msg = PATCH_SUBMISSION_MSG_2
    if magic_line == MAGIC_LINE_3:
        msg = PATCH_SUBMISSION_MSG_3
    if magic_line == MAGIC_LINE_4:
        msg = PATCH_SUBMISSION_MSG_4

    return magic_line + "\n\n" + msg

def add_bot_comment(pr, magic_line):
    """
    Add the bot comment (magic_line)
    """
    comment = get_comment_str(magic_line)
    pr.create_issue_comment(comment)

def get_timedelta(pr):
    """
    Calculate the time delta between today and the PR created date.
    Returns the tuple of number of days and reamin seconds.
    """

    today = datetime.now()
    delta = today - pr.created_at

    return (delta.days, delta.seconds)

def get_magic_line(body):
    if (body.find(MAGIC_LINE) >= 0):
        return MAGIC_LINE
    if (body.find(MAGIC_LINE_2) >= 0):
        return MAGIC_LINE_2
    if (body.find(MAGIC_LINE_3) >= 0):
        return MAGIC_LINE_3
    if (body.find(MAGIC_LINE_4) >= 0):
        return MAGIC_LINE_4
    return None

def get_latest_comment(pr):
    """
    Search through the comments and find the latest comment
    """
    comments = pr.get_issue_comments()
    logger.info("PR#%s Comment count: %s" % (pr.number, comments.totalCount))

    for comment in comments.reversed:
        magic_line = get_magic_line(comment.body)
        if magic_line != None:
            logger.debug("The most recent bluez bot comment: %s" % magic_line)
            return magic_line

    logger.debug("No bluez bot comment found")
    return None

def analyze_comments(pr):
    """
    Analzye the comments and identify the next action/comments
    """

    # Calculate the time/day difference
    (days, seconds) = get_timedelta(pr)
    logger.debug("Time Delta: days: %s seconds: %s" % (days, seconds))

    magic_line = get_latest_comment(pr)
    logger.debug("Comment Magic Line: %s" % magic_line)

    return (days, magic_line)

def update_pull_request(pr, days, magic_line):
    """
    Update the pull request based on the days passed since it was created
    and the latest comment line
    """

    if days < 7:
        logger.debug("Days < 7")
        if magic_line == None:
            logger.debug("New PR without any bot comment. Adding the 1st comment")
            add_bot_comment(pr, MAGIC_LINE)
        else:
            logger.debug("Found bot comment and skip for now: %s" % magic_line)

    if days >= 7 and days < 14:
        logger.debug("7 <= Days < 14")
        if magic_line == MAGIC_LINE_2 or magic_line == MAGIC_LINE_3:
            logger.debug("Found bot commnet and skip for now: %s" % magic_line)
        else:
            if magic_line == MAGIC_LINE:
                logger.debug("Found 1st comment. Adding the 2nd comment")
                add_bot_comment(pr, MAGIC_LINE_2)
            else:
                logger.debug("Old but no comment. Adding the comment #3")
                add_bot_comment(pr, MAGIC_LINE_3)

    if days > 14:
        logger.debug("Days > 14")
        logger.debug("PR is more than 2 weeks and close the PR")
        add_bot_comment(pr, MAGIC_LINE_4)
        logger.debug("Close the PR")
        pr.edit(state="closed")

def manage_pr(github_repo):
    """
    Manage PR
    """

    pr_list = github_repo.get_pulls(state="open")

    logger.info("Pull Request count: %s(open)" % pr_list.totalCount)

    # Handle each PR
    for pr in pr_list:
        logger.debug("Check PR#%s" % pr.number)

        (opened_days, latest_comment) = analyze_comments(pr)

        # Update the PR
        update_pull_request(pr, opened_days, latest_comment)

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

