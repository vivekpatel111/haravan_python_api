import haravan
from test.test_helper import TestCase
from pyactiveresource.activeresource import ActiveResource
from mock import patch
import threading

class BaseTest(TestCase):

    @classmethod
    def setUpClass(self):
        self.session1 = haravan.Session('shop1.myharavan.com', 'token1')
        self.session2 = haravan.Session('shop2.myharavan.com', 'token2')

    def setUp(self):
        super(BaseTest, self).setUp()

    def tearDown(self):
        haravan.HaravanResource.clear_session()

    def test_activate_session_should_set_site_and_headers_for_given_session(self):
        haravan.HaravanResource.activate_session(self.session1)

        self.assertIsNone(ActiveResource.site)
        self.assertEqual('https://shop1.myharavan.com/admin', haravan.HaravanResource.site)
        self.assertEqual('https://shop1.myharavan.com/admin', haravan.Shop.site)
        self.assertIsNone(ActiveResource.headers)
        self.assertEqual('token1', haravan.HaravanResource.headers['X-Haravan-Access-Token'])
        self.assertEqual('token1', haravan.Shop.headers['X-Haravan-Access-Token'])

    def test_clear_session_should_clear_site_and_headers_from_Base(self):
        haravan.HaravanResource.activate_session(self.session1)
        haravan.HaravanResource.clear_session()

        self.assertIsNone(ActiveResource.site)
        self.assertIsNone(haravan.HaravanResource.site)
        self.assertIsNone(haravan.Shop.site)

        self.assertIsNone(ActiveResource.headers)
        self.assertFalse('X-Haravan-Access-Token' in haravan.HaravanResource.headers)
        self.assertFalse('X-Haravan-Access-Token' in haravan.Shop.headers)

    def test_activate_session_with_one_session_then_clearing_and_activating_with_another_session_shoul_request_to_correct_shop(self):
        haravan.HaravanResource.activate_session(self.session1)
        haravan.HaravanResource.clear_session()
        haravan.HaravanResource.activate_session(self.session2)

        self.assertIsNone(ActiveResource.site)
        self.assertEqual('https://shop2.myharavan.com/admin', haravan.HaravanResource.site)
        self.assertEqual('https://shop2.myharavan.com/admin', haravan.Shop.site)

        self.assertIsNone(ActiveResource.headers)
        self.assertEqual('token2', haravan.HaravanResource.headers['X-Haravan-Access-Token'])
        self.assertEqual('token2', haravan.Shop.headers['X-Haravan-Access-Token'])

    def test_delete_should_send_custom_headers_with_request(self):
        haravan.HaravanResource.activate_session(self.session1)

        org_headers=haravan.HaravanResource.headers
        haravan.HaravanResource.set_headers({'X-Custom': 'abc'})

        with patch('haravan.HaravanResource.connection.delete') as mock:
            url = haravan.HaravanResource._custom_method_collection_url('1', {})
            haravan.HaravanResource.delete('1')
            mock.assert_called_with(url, {'X-Custom': 'abc'})

        haravan.HaravanResource.set_headers(org_headers)

    def test_headers_includes_user_agent(self):
        self.assertTrue('User-Agent' in haravan.HaravanResource.headers)
        t = threading.Thread(target=lambda: self.assertTrue('User-Agent' in haravan.HaravanResource.headers))
        t.start()
        t.join()

    def test_headers_is_thread_safe(self):
        def testFunc():
            haravan.HaravanResource.headers['X-Custom'] = 'abc'
            self.assertTrue('X-Custom' in haravan.HaravanResource.headers)

        t1 = threading.Thread(target=testFunc)
        t1.start()
        t1.join()

        t2 = threading.Thread(target=lambda: self.assertFalse('X-Custom' in haravan.HaravanResource.headers))
        t2.start()
        t2.join()
