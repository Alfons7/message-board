from datetime import datetime
from functools import wraps
from werkzeug.urls import url_parse
from flask import redirect, url_for
from application import current_user

# https://stackoverflow.com/a/1551394/14287659
def time_ago(timestamp):
    """
    Take a Python datetime object representing a time in UTC and 
      return a string like 'one hour ago', 'yesterday' or '3 months ago'.
    Assumes the timestamp object does not represent a future time.
    """
    now = datetime.utcnow()

    if now < timestamp:
        raise ValueError('got a timestamp in the future')

    diff = now - timestamp
    days, seconds = diff.days, diff.seconds
    # print(f"{timestamp=} {now=} {diff=}")
    if days == 0:
        if seconds < 10: 
            return "just now"
        elif seconds < 60:
            return f"{seconds} seconds ago"
        elif seconds < 120:
            return "one minute ago"
        elif seconds < 3600:
            return f"{seconds // 60} minutes ago"
        elif seconds < 7200:
            return "one hour ago"
        else:
            return f"{seconds // 3600} hours ago"
    elif days == 1:
        return "yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 14:
        return "one week ago"
    # days < 28 so that "one month ago" is returned
    # instead of "4 weeks ago" 
    elif days < 28:
        return f"{days // 7} weeks ago"
    elif days < 60:
        return "one month ago"
    # days < 360 so that "one year ago" is returned
    # instead of "12 months ago"
    elif days < 360:
        return f"{days // 30} months ago"
    elif days < 730:
        return "one year ago"
    else:
        return f"{days // 365} years ago"

def not_login_required(f):
    """
    Decorate routes to require the current user is NOT loged in.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_next_page(request):
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return next_page