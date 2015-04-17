import pyactiveresource.connection
from pyactiveresource.activeresource import ActiveResource, ResourceMeta, formats
import haravan.yamlobjects
import haravan.mixins as mixins
import haravan
import threading
import sys
from six.moves import urllib
import six


# Store the response from the last request in the connection object
class HaravanConnection(pyactiveresource.connection.Connection):
    response = None

    def __init__(self, site, user=None, password=None, timeout=None,
                 format=formats.JSONFormat):
        super(HaravanConnection, self).__init__(site, user, password, timeout, format)

    def _open(self, *args, **kwargs):
        self.response = None
        try:
            self.response = super(HaravanConnection, self)._open(*args, **kwargs)
        except pyactiveresource.connection.ConnectionError as err:
            self.response = err.response
            raise
        return self.response

# Inherit from pyactiveresource's metaclass in order to use HaravanConnection
class HaravanResourceMeta(ResourceMeta):

    @property
    def connection(cls):
        """HTTP connection for the current thread"""
        local = cls._threadlocal
        if not getattr(local, 'connection', None):
            # Make sure these variables are no longer affected by other threads.
            local.user = cls.user
            local.password = cls.password
            local.site = cls.site
            local.timeout = cls.timeout
            local.headers = cls.headers
            local.format = cls.format
            if cls.site is None:
                raise ValueError("No haravan session is active")
            local.connection = HaravanConnection(
                cls.site, cls.user, cls.password, cls.timeout, cls.format)
        return local.connection

    def get_user(cls):
        return getattr(cls._threadlocal, 'user', HaravanResource._user)

    def set_user(cls, value):
        cls._threadlocal.connection = None
        HaravanResource._user = cls._threadlocal.user = value

    user = property(get_user, set_user, None,
                    "The username for HTTP Basic Auth.")

    def get_password(cls):
        return getattr(cls._threadlocal, 'password', HaravanResource._password)

    def set_password(cls, value):
        cls._threadlocal.connection = None
        HaravanResource._password = cls._threadlocal.password = value

    password = property(get_password, set_password, None,
                        "The password for HTTP Basic Auth.")

    def get_site(cls):
        return getattr(cls._threadlocal, 'site', HaravanResource._site)

    def set_site(cls, value):
        cls._threadlocal.connection = None
        HaravanResource._site = cls._threadlocal.site = value
        if value is not None:
            parts = urllib.parse.urlparse(value)
            if parts.username:
                cls.user = urllib.parse.unquote(parts.username)
            if parts.password:
                cls.password = urllib.parse.unquote(parts.password)

    site = property(get_site, set_site, None,
                    'The base REST site to connect to.')

    def get_timeout(cls):
        return getattr(cls._threadlocal, 'timeout', HaravanResource._timeout)

    def set_timeout(cls, value):
        cls._threadlocal.connection = None
        HaravanResource._timeout = cls._threadlocal.timeout = value

    timeout = property(get_timeout, set_timeout, None,
                       'Socket timeout for HTTP requests')

    def get_headers(cls):
        if not hasattr(cls._threadlocal, 'headers'):
            cls._threadlocal.headers = HaravanResource._headers.copy()
        return cls._threadlocal.headers

    def set_headers(cls, value):
        cls._threadlocal.headers = value

    headers = property(get_headers, set_headers, None,
                       'The headers sent with HTTP requests')

    def get_format(cls):
        return getattr(cls._threadlocal, 'format', HaravanResource._format)

    def set_format(cls, value):
        cls._threadlocal.connection = None
        HaravanResource._format = cls._threadlocal.format = value

    format = property(get_format, set_format, None,
                      'Encoding used for request and responses')


@six.add_metaclass(HaravanResourceMeta)
class HaravanResource(ActiveResource, mixins.Countable):
    _format = formats.JSONFormat
    _threadlocal = threading.local()
    _headers = {'User-Agent': 'HaravanPythonAPI/%s Python/%s' % (haravan.VERSION, sys.version.split(' ', 1)[0])}

    def __init__(self, attributes=None, prefix_options=None):
        if attributes is not None and prefix_options is None:
            prefix_options, attributes = self.__class__._split_options(attributes)
        return super(HaravanResource, self).__init__(attributes, prefix_options)

    def is_new(self):
        return not self.id

    def _load_attributes_from_response(self, response):
        if response.body.strip():
            self._update(self.__class__.format.decode(response.body))

    @classmethod
    def activate_session(cls, session):
        cls.site = session.site
        cls.user = None
        cls.password = None
        cls.headers['X-Haravan-Access-Token'] = session.token

    @classmethod
    def clear_session(cls):
        cls.site = None
        cls.user = None
        cls.password = None
        cls.headers.pop('X-Haravan-Access-Token', None)
