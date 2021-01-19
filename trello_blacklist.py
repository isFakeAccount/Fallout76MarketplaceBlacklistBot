import re

import trello

import CONFIG
import bot_responses


# To extract the text from curly brackets
def extract_frm_curly_brackets(input_text):
    # Check for the curly braces
    return re.findall(r"\{(.*)?\}", input_text)


# Checks the blacklist for keywords that appear in comment
# or checks for the author of comment
def check_comment_in_blacklist(comment):
    # Checks for curly braces
    # The escaping is removed so both fancy pants and markdown editor have same text
    output = extract_frm_curly_brackets(comment.body.replace("\\", ""))
    blacklist_result = list()
    # If the comment has query, only then it searches and replies to the user
    if len(output) > 0:
        for query in output:
            blacklist_result.append(search_in_blacklist(query.strip()))
        bot_responses.comment_blacklist_search_result_for_query(output, blacklist_result, comment)

    # checks for the author of the comment
    blacklist_result = search_in_blacklist(comment.author.name)
    # If the search returns something
    if len(blacklist_result) > 0:
        bot_responses.comment_blacklist_search_result_auto_check(comment.author.name, blacklist_result, comment)


# Check for the author of submission in blacklist
def check_submission_in_blacklist(submission):
    # Search Request cannot be made in submissions
    blacklist_result = search_in_blacklist(submission.author.name)
    # If the search returns something
    if len(blacklist_result) > 0:
        bot_responses.comment_blacklist_search_result_auto_check(submission.author.name, blacklist_result, submission)


# Removes the archived cards from list
def delete_archived_cards_and_check_desc(search_result, search_query):
    for card in search_result:
        # Some search query returns the boards and the members which creates issue later
        if card.__class__ != trello.Card:
            search_result.remove(card)
            continue
        # closed means the card is archived
        if card.closed:
            search_result.remove(card)
        # Double check to make sure that search query is in card description
        if search_query.lower() not in card.description.lower().replace("\\", ""):
            search_result.remove(card)
    return search_result


# Searches in trello board using trello api and return the search result in a list\
# The list is empty if there are no search results
def search_in_blacklist(search_query):
    search_result = list()
    try:
        # escapes the special characters so the search result is exact not from wildcard (e.g '-')
        search_result = CONFIG.trello_client.search(query=re.escape(search_query), cards_limit=10)
        search_result_escaped_underscore = list()
        # If underscore is in search query, we need to search it escaped and non escaped
        if "_" in search_query:
            search_result_escaped_underscore = CONFIG.trello_client.search(
                query=re.escape(search_query.replace("_", "\\_")), cards_limit=10)
        # Adding results from both searches
        search_result = search_result + search_result_escaped_underscore
        # Removing duplicate search results
        search_result = list(set(search_result))
        search_result = delete_archived_cards_and_check_desc(search_result, search_query)
    except NotImplementedError:
        raise NotImplementedError(search_query)
    return search_result
