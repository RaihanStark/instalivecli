from io import BytesIO
import sys
import codecs
import mimetypes
import random
import string

import http.cookiejar as compat_cookiejar
import pickle as compat_pickle

class ClientCookieJar(compat_cookiejar.CookieJar):
    """Custom CookieJar that can be pickled to/from strings
    """
    def __init__(self, cookie_string=None, policy=None):
        """Initialize Cookie Jar

        Args:
            cookie_string (str, optional): cookie_jar string. Defaults to None.
        """
        compat_cookiejar.CookieJar.__init__(self, policy)
        if cookie_string:
            if isinstance(cookie_string, bytes):
                self._cookies = compat_pickle.loads(cookie_string)
            else:
                self._cookies = compat_pickle.loads(cookie_string.encode('utf-8'))

    @property
    def auth_expires(self):
        for cookie in self:
            if cookie.name in ('ds_user_id', 'ds_user'):
                return cookie.expires
        return None

    @property
    def expires_earliest(self):
        """For backward compatibility"""
        """For backward compatibility

        Returns:
            str: cookies expires time 
        """
        return self.auth_expires

    def dump(self, force_cookies=None):
        """pickle cookie_jar to strings

        Args:
            force_cookies (cookie_jar, optional): cookie_jar session. Defaults to None.

        Returns:
            str: pickled cookie_jar strings
        """
        if force_cookies:
            return compat_pickle.dumps(force_cookies)
        return compat_pickle.dumps(self._cookies)
