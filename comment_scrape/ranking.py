import re
import collections
import math
import base64
from comment_scrape.objects import WebPage, Comment

"""Functions that take in an input, and return an approximation of how neat it might be"""

keywords = ['usr', 'user', 'pass', 'admin', 'TODO', 'backup', 'api', 'key', 'secret']

# Compiles a regex that will match any string in the keyword list
keyword_regex = re.compile("(?=("+'|'.join(keywords)+r"))", re.IGNORECASE)


def ingest_pages_and_rank(pages, block_ie=True):
    """Takes a list of pages, and returns a list of comments de duped and sorted by predicted value"""
    comments = []
    for webpage in pages:
        for comment_value in webpage.html_comments:
            tmp_comment = Comment(comment_value, webpage.url)
            tmp_comment.predicted_value = total_value(tmp_comment.comment_text)
            if block_ie and "IE" in tmp_comment.comment_text:
                pass
            else:
                # Find if and what other comment has the same text
                check_if_dup = next((x for x in comments if x.comment_text == tmp_comment.comment_text), None)
                if check_if_dup is not None:
                    check_if_dup.all_urls.append(tmp_comment.source_url)
                else:
                    comments.append(tmp_comment)

    comments.sort(key=lambda x: x.predicted_value, reverse=True)
    return comments


def total_value(comment: str) -> int:
    """Wrapper function that returns the total int of all ranking methods"""
    ret = 0
    ret += shannon_entropy_rank(comment)
    ret += keywords_rank(comment)
    ret += encoding_rank(comment)
    return ret


def shannon_entropy_rank(comment: str) -> int:
    """Returns an int 0-10+, of how random a string is. Designed to find api keys and randomly generated strings"""
    # Original code stolen from https://stackoverflow.com/a/47348423, thanks.
    probabilities = [n_x / len(comment) for x, n_x in collections.Counter(comment).items()]
    e_x = [-p_x * math.log(p_x, 2) for p_x in probabilities]
    # Shannon works better on longer strings, x2 is to make the number bigger (therefor better)
    return sum(e_x)


def keywords_rank(comment: str) -> int:
    """Returns an int 0-10+, based of if the string matches one or more keywords"""

    # In the feature we might have less valuable words, but all of these words are tens to me.
    results = re.findall(keyword_regex, comment)

    if results:
        return len(results) * 10
    else:
        return 0


# noinspection PyBroadException
def encoding_rank(comment: str) -> int:
    """Returns an int 0-10+ based of if the comment looks like valid base64"""

    # Can add more encodings, not sure of the benefits / runtime
    try:
        trash = base64.b64decode(comment).decode("utf-8")
        return 25
    except:
        return 0


def api_key_rank(comment: str) -> int:
    """Returns an int 0-10+, Will match a regex to common api keys"""
    # TODO Implement, get key re's and compile
    # Shannon picks up most weird stuff already
    pass


def uri_credentials_rank(comment: str) -> int:
    pass


if __name__ == '__main__':
    pass
