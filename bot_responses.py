import prawcore


# Replies to comment with text=body
def reply(comment_or_submission, body):
    # Add disclaimer text
    response = body + "\n\n ^(This action was performed by a bot, please contact the mods for any questions. "
    response += "[See disclaimer](https://www.reddit.com/user/Vault-TecTradingCo/comments/lkllre" \
                "/disclaimer_for_rfallout76marketplace/)) "
    try:
        new_comment = comment_or_submission.reply(response)
        new_comment.mod.distinguish(how="yes")
        new_comment.mod.lock()
    except prawcore.exceptions.Forbidden:
        pass


# Get all labels from the trello card
def get_all_labels(trello_card):
    # If there are no labels for card
    if trello_card.labels is None:
        return "BLACKLISTED"
    # Otherwise return all label names in string
    labels = ""
    for label in trello_card.labels:
        labels += label.name + ", "
    return labels[:-2]


# Comments the blacklist search result for automatic check that bot performs on the users
# whenever they submit a post or comment
def comment_blacklist_search_result_auto_check(username, blacklist, comment_or_submission):
    response_text = "The user *" + username + "* has been found on blacklist " + str(len(blacklist)) + " "
    response_text = response_text + "time(s). The links for each time when the user appeared in blacklist are:\n\n"
    for item in blacklist:
        try:
            # Url of card/s
            response_text = response_text + "[" + get_all_labels(
                item) + ": " + item.name + "](" + item.short_url + ")\n\n"
        except Exception:
            response_text += "Error: " + username + "\n\n"
            print("Error: " + username)
    response_text = response_text + "^(Please check each link to verify.)\n\n"
    reply(comment_or_submission, response_text)


# Comments the blacklist search result for search queries that are requested by the users
def comment_blacklist_search_result_for_query(query_list, blacklist, comment_or_submission):
    response_text = ""
    usernames_for_positive_result = ""  # stores the usernames which gave positive search result in string
    positive_result_usernames_list = []  # stores the usernames which gave positive search result in list
    positive_results = []  # # stores the results of positive result usernames
    negative_results_usernames_list = []  # stores the usernames which gave negative search result in string
    usernames_for_negative_result = ""  # stores the usernames which gave negative search result in list
    # Iterate over each user name in query list
    for i in range(len(query_list)):
        # If that username gave positive search result
        if len(blacklist[i]) > 0:
            usernames_for_positive_result += query_list[i] + ", "
            positive_result_usernames_list.append(query_list[i])
            positive_results.append(blacklist[i])
        # If that username gave negative search result
        else:
            usernames_for_negative_result += query_list[i] + ", "
            negative_results_usernames_list.append(blacklist[i])
    # If there are users that had positive search result
    if len(positive_result_usernames_list) > 0:
        response_text += "The user(s) *\"" + usernames_for_positive_result[:-2] + "\"* has/have been found on blacklist"
        response_text += ". The links for each time when the user appeared in blacklist are:\n\n"
        # Iterate over each user
        for i in range(len(positive_result_usernames_list)):
            # Iterate over that user's trello search result as result could have multiple cards
            for positive_result in positive_results[i]:
                response_text = response_text + "[" + get_all_labels(positive_result) + ": " + positive_result.name + \
                                " **(" + positive_result_usernames_list[
                                    i] + ")**](" + positive_result.short_url + ")\n\n"
        response_text = response_text + "^(Please check each link to verify.)\n\n"
    # If there are users that had negative search result
    if len(negative_results_usernames_list) > 0:
        response_text += "The bot has performed a search and has determined that the user(s) *\""
        response_text += usernames_for_negative_result[:-2]
        response_text += "\"* is/are not in present in our blacklist.\n\n^(Please take precautions if the user account"
        response_text += " is very new, has low trade karma or actively delete submissions/comments. You may also check"
        response_text += " their gamertag using the bot commands. If you are doing a high value trade, consider using "
        response_text += "an [official courier](https://www.reddit.com/r/Fallout76Marketplace/wiki/index" \
                         "/trusted_couriers).) "
    reply(comment_or_submission, response_text)
