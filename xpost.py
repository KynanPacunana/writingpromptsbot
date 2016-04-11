import re

import praw
import OAuth2Util

from praw.helpers import _stream_generator
from praw.objects import Comment, Submission

USERNAME = "Kim_MahJong"
POSTSUB = "Kim_MahJongWrites"
READSUB = "WritingPrompts"
MATCH_REGEX = re.compile('\[\]\(#WP\)')
ADD_TO_REGEX = re.compile('\[\]\(#WP "(.+)"\)')

r = praw.Reddit('{0}\'s auto crossposter from {1} to {2}'.format(USERNAME, READSUB, POSTSUB))
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)

user = r.get_redditor(USERNAME)
postto = r.get_subreddit(POSTSUB)
for comment in _stream_generator(user.get_comments, None, 3):
    if comment.subreddit.display_name.lower() == READSUB.lower():
        if MATCH_REGEX.search(comment.body, re.IGNORECASE):
            postto.submit(comment.submission.title, text="{0}\n\n{1}".format(comment.permalink, comment.body), send_replies=True)
        else:
            should_add = ADD_TO_REGEX.search(comment.body, re.IGNORECASE)
            if should_add:
                should_add = should_add.groups()[0].lower()
                try:
                    int(should_add.split('_')[-1], 36)
                    should_add.split('_')[0] in ['t1', 't3']
                except (ValueError, AssertionError):
                    continue
                else:
                    to_reply_to = r.get_info(thing_id=should_add)
                    if not to_reply_to:
                        continue
                    funcattr = 'add_comment' if isinstance(to_reply_to, Submission) else 'reply'
                    getattr(to_reply_to, funcattr)("{0}\n\n{1}".format(comment.permalink, comment.body))
