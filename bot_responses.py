import prawcore


# Replies to comment with text=body
def reply(comment_or_submission, body):
    response = body + "\n\n ^(This action was performed by a bot, please contact the mods for any questions.)"
    try:
        new_comment = comment_or_submission.reply(response)
        new_comment.mod.distinguish(how="yes")
    except prawcore.exceptions.Forbidden:
        pass


# Adds disclaimer text in the comment
def add_disclaimer(response_text, comment_or_submission):
    response_text += "\n\n[See disclaimer]"
    response_text += "(https://www.reddit.com/user/Vault-TecTradingCo/comments/j497xo" \
                     "/disclaimer_for_uvaulttectradingco_bot/) "
    return response_text


def comment_blacklist_search_result(keyword, blacklist, comment_or_submission):
    response_text = "Error! Please message mods!"
    if len(blacklist) > 0:
        response_text = "The user *" + keyword + "* has been found on blacklist " + str(len(blacklist)) + " "
        response_text = response_text + "time(s). The links for each time when the user appeared in blacklist are:\n\n "
        for item in blacklist:
            # Url of card/s
            response_text = response_text + "[" + item.labels[
                0].name + ": " + item.name + "](" + item.short_url + ")\n\n"
            # Checks the description for offense and add them to comment
            desc_list = item.desc.split("\n\n")
            match = [element for element in desc_list if "offense" in element.lower()]
            for element in match:
                response_text += element + "\n\n"
        response_text = response_text + "^(Please check each link to verify.)"
    else:
        response_text = "The bot has performed a search and has determined that the user *\"" + keyword + "\"* is not "
        response_text = response_text + "in present in our blacklist.\n\n^(Please take precautions if the user account "
        response_text = response_text + "is very new, has low trade karma or actively delete submissions/comments. "
        response_text = response_text + "You may also check their gamertag using the bot commands (see Automod pinned "
        response_text = response_text + "comment. If you are doing a high value trade, consider using an official "
        response_text = response_text + "courier. You can find links to all couriers in the subreddit wiki or sidebar.)"
    response_text = add_disclaimer(response_text, comment_or_submission)
    reply(comment_or_submission, response_text)
