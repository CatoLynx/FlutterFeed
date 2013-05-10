# -*- coding: utf-8 -*-
# Strings go here

import flutterfeed_config as config

# Messages etc.
window_title_no_notifications = u"@%(username)s - %(name)s v%(version)s"
window_title_notifications = u"(%(notifications)i) @%(username)s - %(name)s v%(version)s"
auth_url = u"Please visit %s in your browser and authorize this application. If you have a browser installed, the URL should be opened automatically."
verifier_prompt = u"Please enter the verifier code you got from Twitter: "
favorite_notification = u"%s (@%s) favorited your tweet '%s'."
unfavorite_notification = u"%s (@%s) unfavorited your tweet '%s'."
follower_notification = u"%s (@%s) followed you."
statusbar_left = u"@%(username)s | %(followers)i Followers | Following %(following)i | %(tweets)i Tweets | %(favorites)i Favorites"
statusbar_right = u"%(cached_tweets)i tweets cached | %(time)s | %(countdown)s"
countdown_updating = u"Updating..."
countdown = u"Next update in %i:%02i"
prompt = u"[%03.f] > "
prompt_loading = u"[loading] > "
prompt_percentage = u"[%03.f%%] > "
prompt_generic = u"[%s] > "
favorited = u"Favorited \"%s\" by @%s."
unfavorited = u"Unfavorited \"%s\" by @%s."
followed = u"Followed @%s."
unfollowed = u"Unfollowed @%s."
last_tweets_header = u"Last %s tweets by @%s\nHit Enter to reply to the selected tweet."
profile_header = u"%s (@%s)"
profile_item_name = u"Name: %s"
profile_item_location = u"Location: %s"
profile_item_website = u"Website: %s"
profile_item_bio = u"%s"
profile_item_followers = u"Followers: %s"
profile_item_following = u"Following: %s"
profile_item_tweets = u"Tweets: %s"
profile_item_listed = u"Listed: %sx"
profile_item_lang = u"Language: %s"
profile_item_timezone = u"Time zone: %s"
mentions_header = u"Last %s mentions\nHit Enter to reply to the selected tweet."
messages_header = u"Last %s direct messages\nHit Enter to reply to the selected message."
conversation_header = u"Conversation\nHit Enter to reply to all users included in the selected tweet."
rel_both = u"%s <=> %s"
rel_i_follow = u"%s => %s"
rel_following_me = u"%s <= %s"
rel_none = u"%s - %s"
dump_header = u"Tweet Dump\n"
dump_short_code = u"Internal short code: %s"
dump_internal_id = u"Internal Tweet ID: %s"
dump_internal_in_reply_to = u"Internal in reply to status ID: %s"
dump_internal_username = u"Internal username: %s"
dump_internal_text = u"Internal text: %s"
dump_id = u"ID: %s"
dump_in_reply_to = u"In reply to status ID: %s"
dump_author = u"Author: %s"
dump_text = u"Text: %s"
dump_source = u"Source: %s"
trends_header = u"Current Global Trends\nHit Enter to write a tweet about the selected trend."
delete_notification = u"%s deleted their tweet '%s' (%s)."
filtered_word = u"Now filtering out \"%s\"."
filtered_user = u"Now filtering out user @%s."
filtered_client = u"Now filtering out client \"%s\"."
filtered_regex = u"Now filtering out regular expression \"%s\"."
unfiltered_word = u"No longer filtering out \"%s\"."
unfiltered_user = u"No longer filtering out user @%s."
unfiltered_client = u"No longer filtering out client \"%s\"."
unfiltered_regex = u"No longer filtering out regular expression \"%s\"."
word_filter = u"Words currently in word filter:\n\n%s"
user_filter = u"Users currently in user filter:\n\n%s"
client_filter = u"Clients currently in client filter:\n\n%s"
regex_filter = u"Regular expressions currently in regex filter:\n\n%s"
highlighted_word = u"Now highlighting \"%s\"."
highlighted_user = u"Now highlighting user @%s."
highlighted_client = u"Now highlighting client \"%s\"."
highlighted_regex = u"Now highlighting regular expressions \"%s\"."
unhighlighted_word = u"No longer highlighting \"%s\"."
unhighlighted_user = u"No longer highlighting user @%s."
unhighlighted_client = u"No longer highlighting client \"%s\"."
unhighlighted_regex = u"No longer highlighting regular expression \"%s\"."
highlighted_words = u"Words currently highlighted:\n\n%s"
highlighted_users = u"Users currently highlighted:\n\n%s"
highlighted_clients = u"Clients currently highlighted:\n\n%s"
highlighted_regexes = u"Regular expressions currently highlighted:\n\n%s"
message_sent = u"Your direct message has been sent to @%s."
blocked = u"@%s has been blocked."
unblocked = u"@%s has been unblocked."
reported_as_spam = u"@%s has been blocked and reported as spam."
help_header = u"Help"
quit_confirmation = u"Really quit?"
mention_select_action = u"What would you like to do?"
action_reply = u"Reply"
view_conversation = u"View conversation"
use_twitlonger = u"Tweet is longer than 140 characters.\n\nPost it to TwitLonger? (No additional effort for you!)"
use_twextender = u"Tweet is longer than 140 characters.\n\nPost it to TwExtender? (No additional effort for you!)"
twitlonger_protected_account = u"Your account is protected.\nIf you use TwitLonger, everybody who has the link can see this tweet.\n\nContinue anyway?"
twextender_protected_account = u"Your account is protected.\nIf you use TwExtender, everybody who has the link can see this tweet.\n\nContinue anyway?"
afk_mode_enabled = u"AFK mode enabled. Showing only mentions, direct messages, favorite and follower notifications."
afk_mode_disabled = u"AFK mode disabled. Showing all new tweets."
deleted = u"Your tweet \"%s\" has been deleted."
message_deleted = u"Your direct message \"%s\" to @%s has been deleted."
lists_header = u"Your lists\nHit Enter to view the details of the selected list."
list_details_header = u"%s"
list_details_item_description = u"%s"
list_details_item_privacy = u"Privacy: %s"
list_details_item_members = u"Members: %s"
list_details_item_subscribers = u"Subscribers: %s"
button_members = u"View members"
button_edit = u"Edit"
update_available = u"An update for %s is available!\n\nLatest version: %s\n\nChanges include:\n%s\n\nGo to http://www.mezgrman.de/flutterfeed to download it."
button_yes = u"Yes"
button_no = u"No"
button_ok = u"OK"
list_members_header = u"Members of \"%s\"\nHit Enter to remove the selected user from the list."
list_members_item = u"%s (@%s)"
edit_profile_header = u"Edit your profile"
caption_name = u"Name:"
caption_location = u"Location:"
caption_website = u"Website:"
caption_bio = u"Bio:"
profile_updated = u"Your profile has been updated."
button_edit_profile = u"Edit profile"
reconnected_after_stream_error = u"Successfully reconnected after a stream error."
edit_list_header = u"Edit your list \"%s\""
caption_privacy = u"Privacy (public or private):"
caption_description = u"Description:"
list_updated = u"Your list \"%s\" has been updated."
remove_user_from_list = u"Remove @%s from your list \"%s\"?"
list_member_removed = u"@%s has been removed from your list \"%s\"."
button_add_member = u"Add member"
button_delete_list = u"Delete list"
add_list_member = u"Add a member to your list \"%s\""
list_member_added = u"@%s has been added to your list \"%s\"."
delete_list = u"Do you really want to delete your list \"%s\"?"
list_deleted = u"Your list \"%s\" has been deleted."
create_list_header = u"Create a new list"
list_created = u"Your list \"%s\" has been created."
caption_username = u"Username:"
message_popup_notification = u"New direct message from @%s"
notification_title = u"%s (@%s)"
args_nobackfill = u"Turn off timeline backfilling on startup"
args_manual = u"Run in \"manual\" mode (no automatic timeline refreshing)"
args_tweet = u"Send a tweet with the given text and exit"
args_keywords = u"Comma separated list of keywords to start a stream for instead of starting the user's timeline stream"
args_users = u"Comma separated list of user IDs to start a stream for instead of starting the user's timeline stream"
args_locations = u"Comma separated list of location bounding box coordinates to start a stream for instead of starting the user's timeline stream"
args_database = u"The database file to use"
args_account = u"The account / profile to use. If not specified, use the default account. If no account with the given name is found, it is created."
sync_confirmation = u"This action will unfollow %i and follow %i people, performing %i API calls.\n\nAre you sure you want to continue?"
sync_complete = u"Synchronization complete. %i actions performed."
sync_profile_confirmation = u"This action will copy the profile data of @%(screen_name)s to your profile.\n\nAre you sure you want to continue?"
sync_profile_complete = u"Profile synchronization complete."

# More 'internal' strings
tweet_prefix = u"%s: "
direct_message_prefix = u"[DM] %s: "
tweet_code_prefix = u"%s "
direct_message_code_prefix = u"%s "
reply = u"@%s %s"
retweet_prefix = u"%s ↻ %s: "
retweet_scheme = u"%s RT @%s: %s"
rel_both = u"%s ↔ %s"
rel_i_follow = u"%s → %s"
rel_following_me = u"%s ← %s"
rel_none = u"%s – %s"
replyall = u"%s %s"
block_title_scheme = u" %s "
message = u"%s"
tweet_list_format = u"%s %s"
mention_list_format = u"%s %s: %s"
conversation_list_format = u"%s %s: %s"
message_list_format_received = u"%s %s: %s"
message_list_format_sent = u"%s To %s: %s"
sent_message_prefix = "To "
startup_text = u"%(client_name)s v%(version)s - %(client_description)s\n(c) 2012 @Mezgrman.\nTry /help for a list of available commands.\nInvoke with --help or -h to see possible command line arguments.\nHave fun and tweet me if you like it! :)" % {'client_name': config.system.client_name, 'version': config.system.version, 'client_description': config.system.client_description}
quit_text = u"Thanks for using %(client_name)s! Goodbye!" % {'client_name': config.system.client_name}
help_header = u"Command help (press Esc to hide)\nCommand syntax: /command parameter1 parameter2 | alternative to parameter2 [optional parameter3]"
help_entries = [
	("Ctrl + X", "Quit the client."),
	("/rt code [text]", "Retweet the tweet with the given short code. If text is given, do a commented RT in the form \"comment RT @user: original tweet\"."),
	("/fav code", "Favorite the tweet with the given short code."),
	("/unfav code", "Favorite the tweet with the given short code."),
	("/follow username", "Follow the given user."),
	("/unfollow username", "Unfollow the given user."),
	("/last [username]", "Show the last tweets by the given user. If no user is given, show your own last tweets."),
	("/profile [username]", "Show the profile information of the given user. If no user is given, show your own profile."),
	("/reply code text", "Reply to the author of the tweet or direct message with the given short code.\nThis command does NOT send direct messages!"),
	("/me", "Show your last mentions."),
	("/conv code [count]", "Show the previous [count] messages of the conversation the tweet with the given short code is part of."),
	("/rel user1 [user2]", "Show the relationship between you and user1 or user1 and user2 if user2 is given."),
	("/del code", "Delete the tweet with the given short code."),
	("/rall code text", "Reply to all people mentioned in the tweet with the given short code."),
	("/trends", "Show the current worldwide trends."),
	("/logout", "Log out of the client."),
	("/clear", "Clear the feed window."),
	("/filterword word", "Add the given word to the word filter."),
	("/filteruser username", "Add the given user to the user filter."),
	("/filterclient clientname", "Add the given client to the client filter."),
	("/filterregex regex", "Add the given regular expression to the regex filter."),
	("/unfilterword word", "Remove the given word from the word filter."),
	("/unfilteruser username", "Remove the given user from the user filter."),
	("/unfilterclient clientname", "Remove the given client from the client filter."),
	("/unfilterregex regex", "Remove the given regular expression from the client filter."),
	("/wordfilter", "Show all words that are currently in the word filter."),
	("/userfilter", "Show all users that are currently in the user filter."),
	("/clientfilter", "Show all clients that are currently in the client filter."),
	("/regexfilter", "Show all regular expressions that are currently in the regex filter."),
	("/highlightword word", "Highlight tweets containing the given word."),
	("/highlightuser username", "Highlight tweets from the given user."),
	("/highlightclient clientname", "Highlight tweets coming from the given client."),
	("/highlightregex regex", "Highlight tweets matching the given regular expression."),
	("/unhighlightword word", "Stop highlighting tweets containing the given word."),
	("/unhighlightuser username", "Stop highlighting tweets from the given user."),
	("/unhighlightclient clientname", "Stop highlighting tweets coming from the given client."),
	("/unhighlightregex regex", "Stop highlighting tweets matching the given regular expression."),
	("/highlightedwords", "Show all words that are currently highlighted."),
	("/highlightedusers", "Show all users that are currently highlighted."),
	("/highlightedclients", "Show all clients that are currently highlighted."),
	("/highlightedregexes", "Show all regular expressions that are currently highlighted."),
	("/dms", "Show your last direct messages."),
	("/dm username | code text", "Send a direct message to the given user or the author of the direct message or tweet with the given short code."),
	("/block username", "Block the given user."),
	("/unblock username", "Unblock the given user."),
	("/report username", "Block and report the given user as spam."),
	("/afkon", "Turn on AFK mode. In AFK mode, only mentions, direct messages, favorite, unvaforite and follower notifications are shown."),
	("/afkoff", "Turn off AFK mode. All new tweets and events are shown."),
	("/refresh", "Manually refresh the timeline."),
	("/sync username", "Synchronize your 'following' with the given account. Use with caution, it will unfollow people and might get you blocked from the API!"),
	("/syncprofile username", "Synchronize your profile with the given account. Use wisely, as it is effectively a way to impersonate someone else!"),
	#("/lists", "Show your lists."),
	#("/createlist", "Show a dialog to create a new list."),
	("/help", "Show this help."),
]

# Errors
timeout = u"Timeout. Reconnecting in %i seconds..."
stream_error = u"Stream error. Reconnecting in %i seconds..."
stream_reconnecting = u"Reconnecting..."
api_error = u"API Error #%i: %s"
generic_error = u"Generic Error."
data_required = u"Not enough arguments for command '%s'."
invalid_short_code = u"Invalid short code '%s' in command '%s %s'."
invalid_command = u"%s: Invalid command."
filter_word_error = u"\"%s\" is already in the word filter."
filter_user_error = u"@%s is already in the user filter."
filter_client_error = u"\"%s\" is already in the client filter."
filter_regex_error = u"\"%s\" is already in the regular expression filter."
unfilter_word_error = u"\"%s\" is not in the word filter."
unfilter_user_error = u"@%s is not in the user filter."
unfilter_client_error = u"\"%s\" is not in the client filter."
unfilter_regex_error = u"\"%s\" is not in the regular expression filter."
highlight_word_error = u"\"%s\" is already highlighted."
highlight_user_error = u"@%s is already highlighted."
highlight_client_error = u"\"%s\" is already highlighted."
highlight_regex_error = u"Regular expression \"%s\" is already highlighted."
unhighlight_word_error = u"\"%s\" is not highlighted."
unhighlight_user_error = u"@%s is not highlighted."
unhighlight_client_error = u"\"%s\" is not highlighted."
unhighlight_regex_error = u"Regular expression \"%s\" is not highlighted."
twitlonger_error = u"Error posting the tweet to TwitLonger: %s"
twextender_error = u"Error posting the tweet to TwExtender: %s"
afk_mode_already_enabled = u"AFK mode is already enabled."
afk_mode_not_enabled = u"AFK mode is not enabled."
retweet_failed = u"You cannot retweet this tweet.\n\nIt might be from a protected user or you might have already retweeted it."
feature_not_yet_implemented = u"This feature has not yet been implemented."
