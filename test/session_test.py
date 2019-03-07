import haravan
from test.test_helper import TestCase
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import time
from six.moves import urllib

class SessionTest(TestCase):

    def test_not_be_valid_without_a_url(self):
        session = haravan.Session("", "any-token")
        self.assertFalse(session.valid)

    def test_not_be_valid_without_token(self):
        session = haravan.Session("testshop.myharavan.com")
        self.assertFalse(session.valid)

    def test_be_valid_with_any_token_and_any_url(self):
        session = haravan.Session("testshop.myharavan.com", "any-token")
        self.assertTrue(session.valid)

    def test_not_raise_error_without_params(self):
        session = haravan.Session("testshop.myharavan.com", "any-token")

    def test_raise_error_if_params_passed_but_signature_omitted(self):
        with self.assertRaises(haravan.ValidationException):
            session = haravan.Session("testshop.myharavan.com")
            token = session.request_token({'code':'any_code', 'foo': 'bar', 'timestamp':'1234'})

    def test_setup_api_key_and_secret_for_all_sessions(self):
        haravan.Session.setup(api_key="My test key", secret="My test secret")
        self.assertEqual("My test key", haravan.Session.api_key)
        self.assertEqual("My test secret", haravan.Session.secret)

    def test_use_https_protocol_by_default_for_all_sessions(self):
        self.assertEqual('https', haravan.Session.protocol)

    def test_temp_reset_haravan_HaravanResource_site_to_original_value(self):
        haravan.Session.setup(api_key="key", secret="secret")
        session1 = haravan.Session('fakeshop.myharavan.com', 'token1')
        haravan.HaravanResource.activate_session(session1)

        assigned_site = ""
        with haravan.Session.temp("testshop.myharavan.com", "any-token"):
            assigned_site = haravan.HaravanResource.site

        self.assertEqual('https://testshop.myharavan.com/admin', assigned_site)
        self.assertEqual('https://fakeshop.myharavan.com/admin', haravan.HaravanResource.site)

    def test_temp_reset_haravan_HaravanResource_site_to_original_value_when_using_a_non_standard_port(self):
        haravan.Session.setup(api_key="key", secret="secret")
        session1 = haravan.Session('fakeshop.myharavan.com:3000', 'token1')
        haravan.HaravanResource.activate_session(session1)

        assigned_site = ""
        with haravan.Session.temp("testshop.myharavan.com", "any-token"):
            assigned_site = haravan.HaravanResource.site

        self.assertEqual('https://testshop.myharavan.com/admin', assigned_site)
        self.assertEqual('https://fakeshop.myharavan.com:3000/admin', haravan.HaravanResource.site)

    def test_temp_works_without_currently_active_session(self):
        haravan.HaravanResource.clear_session()

        assigned_site = ""
        with haravan.Session.temp("testshop.myharavan.com", "any-token"):
            assigned_site = haravan.HaravanResource.site

        self.assertEqual('https://testshop.myharavan.com/admin', assigned_site)
        self.assertEqual('https://None/admin', haravan.HaravanResource.site)

    def test_create_permission_url_returns_correct_url_with_single_scope_no_redirect_uri(self):
        haravan.Session.setup(api_key="My_test_key", secret="My test secret")
        session = haravan.Session('http://localhost.myharavan.com')
        scope = ["write_products"]
        permission_url = session.create_permission_url(scope)
        self.assertEqual("https://localhost.myharavan.com/admin/oauth/authorize?client_id=My_test_key&scope=write_products", self.normalize_url(permission_url))

    def test_create_permission_url_returns_correct_url_with_single_scope_and_redirect_uri(self):
        haravan.Session.setup(api_key="My_test_key", secret="My test secret")
        session = haravan.Session('http://localhost.myharavan.com')
        scope = ["write_products"]
        permission_url = session.create_permission_url(scope, "my_redirect_uri.com")
        self.assertEqual("https://localhost.myharavan.com/admin/oauth/authorize?client_id=My_test_key&redirect_uri=my_redirect_uri.com&scope=write_products", self.normalize_url(permission_url))

    def test_create_permission_url_returns_correct_url_with_dual_scope_no_redirect_uri(self):
        haravan.Session.setup(api_key="My_test_key", secret="My test secret")
        session = haravan.Session('http://localhost.myharavan.com')
        scope = ["write_products","write_customers"]
        permission_url = session.create_permission_url(scope)
        self.assertEqual("https://localhost.myharavan.com/admin/oauth/authorize?client_id=My_test_key&scope=write_products%2Cwrite_customers", self.normalize_url(permission_url))

    def test_create_permission_url_returns_correct_url_with_no_scope_no_redirect_uri(self):
        haravan.Session.setup(api_key="My_test_key", secret="My test secret")
        session = haravan.Session('http://localhost.myharavan.com')
        scope = []
        permission_url = session.create_permission_url(scope)
        self.assertEqual("https://localhost.myharavan.com/admin/oauth/authorize?client_id=My_test_key&scope=", self.normalize_url(permission_url))

    def test_raise_exception_if_code_invalid_in_request_token(self):
        haravan.Session.setup(api_key="My test key", secret="My test secret")
        session = haravan.Session('http://localhost.myharavan.com')
        self.fake(None, url='https://localhost.myharavan.com/admin/oauth/access_token', method='POST', code=404, body='{"error" : "invalid_request"}', has_user_agent=False)

        with self.assertRaises(haravan.ValidationException):
            session.request_token({'code':'any-code', 'timestamp':'1234'})

        self.assertFalse(session.valid)

    def test_return_site_for_session(self):
        session = haravan.Session("testshop.myharavan.com", "any-token")
        self.assertEqual("https://testshop.myharavan.com/admin", session.site)

    def test_hmac_calculation(self):
        # Test using the secret and parameter examples given in the Haravan API documentation.
        haravan.Session.secret='hush'
        params = {
          'shop': 'some-shop.myharavan.com',
          'code': 'a94a110d86d2452eb3e2af4cfb8a3828',
          'timestamp': '1337178173',
          'signature': '6e39a2ea9e497af6cb806720da1f1bf3',
          'hmac': 'b0a5dd62e8a070491b40d5f5b6f8c82263604442293fc7a8ee21445f4263def4',
        }
        self.assertEqual(haravan.Session.calculate_hmac(params), params['hmac'])

    def test_return_token_if_hmac_is_valid(self):
        haravan.Session.secret='secret'
        params = {'code': 'any-code', 'timestamp': time.time()}
        hmac = haravan.Session.calculate_hmac(params)
        params['hmac'] = hmac

        self.fake(None, url='https://localhost.myharavan.com/admin/oauth/access_token', method='POST', body='{"access_token" : "token"}', has_user_agent=False)
        session = haravan.Session('http://localhost.myharavan.com')
        token = session.request_token(params)
        self.assertEqual("token", token)

    def test_return_token_if_hmac_is_valid_but_signature_also_provided(self):
        haravan.Session.secret='secret'
        params = {'code': 'any-code', 'timestamp': time.time(), 'signature': '6e39a2'}
        hmac = haravan.Session.calculate_hmac(params)
        params['hmac'] = hmac

        self.fake(None, url='https://localhost.myharavan.com/admin/oauth/access_token', method='POST', body='{"access_token" : "token"}', has_user_agent=False)
        session = haravan.Session('http://localhost.myharavan.com')
        token = session.request_token(params)
        self.assertEqual("token", token)

    def test_raise_error_if_hmac_is_invalid(self):
        haravan.Session.secret='secret'
        params = {'code': 'any-code', 'timestamp': time.time()}
        params['hmac'] = 'a94a110d86d2452e92a4a64275b128e9273be3037f2c339eb3e2af4cfb8a3828'

        with self.assertRaises(haravan.ValidationException):
            session = haravan.Session('http://localhost.myharavan.com')
            session = session.request_token(params)

    def test_raise_error_if_hmac_does_not_match_expected(self):
        haravan.Session.secret='secret'
        params = {'foo': 'hello', 'timestamp': time.time()}
        hmac = haravan.Session.calculate_hmac(params)
        params['hmac'] = hmac
        params['bar'] = 'world'
        params['code'] = 'code'

        with self.assertRaises(haravan.ValidationException):
            session = haravan.Session('http://localhost.myharavan.com')
            session = session.request_token(params)

    def test_raise_error_if_timestamp_is_too_old(self):
        haravan.Session.secret='secret'
        one_day = 24 * 60 * 60
        params = {'code': 'any-code', 'timestamp': time.time()-(2*one_day)}
        hmac = haravan.Session.calculate_hmac(params)
        params['hmac'] = hmac

        with self.assertRaises(haravan.ValidationException):
            session = haravan.Session('http://localhost.myharavan.com')
            session = session.request_token(params)

    def normalize_url(self, url):
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)
        query = "&".join(sorted(query.split("&")))
        return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
