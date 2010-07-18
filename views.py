import datetime
from email.Utils import parsedate

class DateParser():
    def _parsedate(date):
        """
        Parse date and return datetime object.
        @param date RFC 2833 form data
        @return datetime object
        """
        return datetime.datetime(*parsedate(date)[0:6])
