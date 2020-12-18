import unittest
from datetime import datetime, timedelta
from helpers import time_ago
from application import app, db
from models import User, Post

def mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=0):
    """
    Creates a datetime object, expressing a utc time in the past, 
    the given number of days and seconds ago.
    """
    return datetime.utcnow() - timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)

# inputs and expected outputs to test the time_ago helper function
timestamps_and_strings = [
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=0), "just now"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=9), "just now"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=10), "10 seconds ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=59), "59 seconds ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=60), "one minute ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=119), "one minute ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=120), "2 minutes ago"),
    (mk_timestamp(weeks=0, days=0, hours=1, minutes=0, seconds=0), "one hour ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=3600), "one hour ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=7199), "one hour ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=7200), "2 hours ago"),
    (mk_timestamp(weeks=0, days=0, hours=2, minutes=0, seconds=0), "2 hours ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=86399), "23 hours ago"),
    (mk_timestamp(weeks=0, days=0, hours=23, minutes=0, seconds=0), "23 hours ago"),
    (mk_timestamp(weeks=0, days=0, hours=0, minutes=0, seconds=86400), "yesterday"),
    (mk_timestamp(weeks=0, days=0, hours=24, minutes=0, seconds=0), "yesterday"),
    (mk_timestamp(weeks=0, days=1, hours=0, minutes=0, seconds=0), "yesterday"),
    (mk_timestamp(weeks=0, days=2, hours=0, minutes=0, seconds=0), "2 days ago"),
    (mk_timestamp(weeks=0, days=6, hours=0, minutes=0, seconds=0), "6 days ago"),
    (mk_timestamp(weeks=0, days=7, hours=0, minutes=0, seconds=0), "one week ago"),
    (mk_timestamp(weeks=0, days=13, hours=0, minutes=0, seconds=0), "one week ago"),
    (mk_timestamp(weeks=1, days=0, hours=0, minutes=0, seconds=0), "one week ago"),
    (mk_timestamp(weeks=0, days=14, hours=0, minutes=0, seconds=0), "2 weeks ago"),
    (mk_timestamp(weeks=2, days=0, hours=0, minutes=0, seconds=0), "2 weeks ago"),
    (mk_timestamp(weeks=0, days=27, hours=0, minutes=0, seconds=0), "3 weeks ago"),
    (mk_timestamp(weeks=3, days=0, hours=0, minutes=0, seconds=0), "3 weeks ago"),
    (mk_timestamp(weeks=0, days=28, hours=0, minutes=0, seconds=0), "one month ago"),
    (mk_timestamp(weeks=0, days=59, hours=0, minutes=0, seconds=0), "one month ago"),
    (mk_timestamp(weeks=4, days=0, hours=0, minutes=0, seconds=0), "one month ago"),
    (mk_timestamp(weeks=0, days=60, hours=0, minutes=0, seconds=0), "2 months ago"),
    (mk_timestamp(weeks=0, days=359, hours=0, minutes=0, seconds=0), "11 months ago"),
    (mk_timestamp(weeks=0, days=360, hours=0, minutes=0, seconds=0), "one year ago"),
    (mk_timestamp(weeks=0, days=729, hours=0, minutes=0, seconds=0), "one year ago"),
    (mk_timestamp(weeks=0, days=730, hours=0, minutes=0, seconds=0), "2 years ago"),
    (mk_timestamp(weeks=0, days=1094, hours=0, minutes=0, seconds=0), "2 years ago"),
    (mk_timestamp(weeks=0, days=1095, hours=0, minutes=0, seconds=0), "3 years ago")
]

class HelpersTest(unittest.TestCase):
    def test_time_ago_with_present_and_past_timestamps(self):
        for timestamp, string in timestamps_and_strings:
            self.assertEqual(time_ago(timestamp), string)

    def test_time_ago_with_furure_timestamp(self):
        future_timestamp = datetime.utcnow() + timedelta(seconds=1)
        with self.assertRaises(ValueError):
            time_ago(future_timestamp)
