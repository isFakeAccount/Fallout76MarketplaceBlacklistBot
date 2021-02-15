import json
import time
import traceback

import praw
import prawcore
import requests
import trello

import CONFIG
import trello_blacklist

# Only works in the subreddit mentioned in CONFIG and when bot is mentioned explicitly
subreddit = CONFIG.reddit.subreddit(CONFIG.subreddit_name)

# Gets 100 historical comments
comment_stream = subreddit.stream.comments(pause_after=-1, skip_existing=True)
# Gets 100 historical submission
submission_stream = subreddit.stream.submissions(pause_after=-1, skip_existing=True)
# inbox stream
mentions_stream = praw.models.util.stream_generator(CONFIG.reddit.inbox.mentions, pause_after=-1, skip_existing=True)

# The numbers of failed attempt to connect to reddit
failed_attempt = 1

print('Bot has started running...')


# Send message to discord channel
def send_message_to_discord(message_param):
    data = {"content": message_param, "username": CONFIG.bot_name}
    output = requests.post(CONFIG.discord_webhooks, data=json.dumps(data), headers={"Content-Type": "application/json"})
    output.raise_for_status()


# Make sure bot run forever
while True:
    try:
        # Gets comments and if it receives None, it switches to posts
        for comment in comment_stream:
            if comment is None or comment.author.name == "AutoModerator":
                break
            trello_blacklist.check_comment_in_blacklist(comment)

        # Gets posts and if it receives None, it switches to mentions
        for submission in submission_stream:
            if submission is None:
                break
            trello_blacklist.check_submission_in_blacklist(submission)

        # Gets mentions and if it receives None, it switches to messages
        for mentions in mentions_stream:
            if mentions is None:
                break
            trello_blacklist.check_comment_in_blacklist(mentions)

        # Resetting failed attempt counter in case the code doesn't throw exception
        failed_attempt = 1
    except Exception as exception:
        # Sends a message to mods in case of error
        tb = traceback.format_exc()
        try:
            send_message_to_discord(tb)
            print(tb)
        except Exception:
            print("Error sending message to discord")

        # In case of server error pause for two minutes
        if isinstance(exception, prawcore.exceptions.ServerError) or isinstance(exception, trello.ResourceUnavailable):
            print("Waiting {} minutes".format(2 * failed_attempt))
            # Try again after a pause
            time.sleep(120 * failed_attempt)
            failed_attempt = failed_attempt + 1

        # Refresh streams
        comment_stream = subreddit.stream.comments(pause_after=-1, skip_existing=True)
        submission_stream = subreddit.stream.submissions(pause_after=-1, skip_existing=True)
        inbox_stream = praw.models.util.stream_generator(CONFIG.reddit.inbox.mentions, pause_after=-1,
                                                         skip_existing=True)
