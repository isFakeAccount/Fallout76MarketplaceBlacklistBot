import re

import trello

import CONFIG
import bot_responses


# To extract the text from curly brackets
def extract_frm_curly_brackets(input_text):
    # Check for the curly braces
    regex_extract = re.search(r"\{(.*)?\}", input_text)
    if regex_extract is not None:
        return regex_extract.group(1)
    return None


# Checks the blacklist for keywords that appear in comment
# or checks for the author of comment
def check_comment_in_blacklist(comment):
    output = extract_frm_curly_brackets(comment.body.replace("\\", ""))
    search_requested = True
    # Checks for curly braces
    if output is not None:
        # Checks for the word enclosed in brackets if any
        search_in_blacklist(output, search_requested, comment)
    search_requested = False
    # checks for the author of the comment
    search_in_blacklist(comment.author.name, search_requested, comment)


# Check for the author of submission in blacklist
def check_submission_in_blacklist(submission):
    search_requested = False
    # Search Request cannot be made in submissions
    search_in_blacklist(submission.author.name, search_requested, submission)


# Removes the archived cards from list
def delete_archived_cards_and_check_desc(search_result, search_query):
    for card in search_result:
        if card.__class__ != trello.Card:
            search_result.remove(card)
            continue
        if card.closed:
            search_result.remove(card)
        # Double check to make sure that search query is in card description
        if search_query.lower() not in card.description.lower().replace("\\", ""):
            search_result.remove(card)
    return search_result


# Searches in trello board using trello api
# search_requested indicates if the search was requested by user or whether it was automatic check
def search_in_blacklist(search_query, search_requested, comment_or_submission):
    search_result = list()
    try:
        # escapes the special characters so the search result is exact not from wildcard (e.g '-')
        # Since re.escape does not work on underscores, we need to manually escape the underscores.
        search_result = CONFIG.trello_client.search(query=re.escape(search_query.replace('_', '\\_')), cards_limit=10)
        search_result = delete_archived_cards_and_check_desc(search_result, search_query)
    except NotImplementedError:
        raise NotImplementedError(search_query)

    # If nothing is returned by search result
    if len(search_result) == 0:
        # If search is requested only then the response is required
        if search_requested:
            bot_responses.comment_blacklist_search_result(search_query, search_result, comment_or_submission)
    # If search result returns something
    else:
        bot_responses.comment_blacklist_search_result(search_query, search_result, comment_or_submission)
