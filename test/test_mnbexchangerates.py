import mock
import unittest

from mnbexchangerates import mnbexchangerates


RESPONSE_VALID = b"""<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
<s:Body>
<GetCurrentExchangeRatesResponse
    xmlns="http://www.mnb.hu/webservices/"
    xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
<GetCurrentExchangeRatesResult>
&lt;MNBCurrentExchangeRates&gt;
&lt;Day date="2018-01-03"&gt;
&lt;Rate unit="1" curr="EUR"&gt;500,000&lt;/Rate&gt;
&lt;/Day&gt;
&lt;/MNBCurrentExchangeRates&gt;
</GetCurrentExchangeRatesResult>
</GetCurrentExchangeRatesResponse>
</s:Body>
</s:Envelope>"""
RESPONSE_INVALID = b"""some invalid response"""
RESPONSE_EMPTY_VALID = b"""<validxml><sometag>aaa</sometag></validxml>"""

CACHE = {'date': '2018-01-03', 'rates': [('1', 'EUR', '600,000')]}
EMPTY_CACHE = None

RESULT_FROM_RESPONSE_VALID = 'MNB exchange rate of  1 EUR = 500,000 HUF  (2018-01-03)'
RESULT_FROM_CACHE = 'MNB exchange rate of  1 EUR = 600,000 HUF  (2018-01-03)'

DEBUG_ON = True
DEBUG_OFF = False


class MNBExchangeRatesTest(unittest.TestCase):

    def setUp(self):
        self.patch_requests = mock.patch('mnbexchangerates.mnbexchangerates.requests')
        self.mock_requests = self.patch_requests.start()
        self.patch_cache = mock.patch('mnbexchangerates.mnbexchangerates.mnbexchangerates_cache')
        self.mock_cache = self.patch_cache.start()
        self.mnb = mnbexchangerates.MNBExchangeRates(DEBUG_ON)
        self.mock_cache.MNBExchangeRateCache.return_value.load.return_value = EMPTY_CACHE

    def tearDown(self):
        self.patch_requests.stop()
        self.patch_cache.stop()
        self.mnb = None

    def _assert_result(self, currency='EUR', expected_result=RESULT_FROM_RESPONSE_VALID):
        result = self.mnb.get_str_of_rate_for_currency(currency)
        self.assertEqual(expected_result, result)

    def _set_request_post_return_value(self, code=200, content=RESPONSE_VALID):
        mock_response = mock.MagicMock()
        mock_response.status_code = code
        mock_response.content = content
        self.mock_requests.post.return_value = mock_response

    def test_get_eur(self):
        self._set_request_post_return_value()
        self._assert_result(currency='EUR', expected_result=RESULT_FROM_RESPONSE_VALID)

    def test_without_debug(self):
        self.mnb = mnbexchangerates.MNBExchangeRates(DEBUG_OFF)
        self._set_request_post_return_value()
        self._assert_result(currency='EUR', expected_result=RESULT_FROM_RESPONSE_VALID)

    def test_wrong_response(self):
        self._set_request_post_return_value(code=404, content='dummy')
        self._assert_result(expected_result='Server response: 404')

    def test_invalid_response_with_valid_status_code(self):
        self._set_request_post_return_value(code=200, content=RESPONSE_INVALID)
        self._assert_result(expected_result='Malformed content received from server')

    def test_empty_valid_response_with_valid_status_code(self):
        self._set_request_post_return_value(code=200, content=RESPONSE_EMPTY_VALID)
        self._assert_result(expected_result='Malformed content received from server')

    def test_with_cache(self):
        self.mock_cache.MNBExchangeRateCache.return_value.load.return_value = CACHE
        self._assert_result(expected_result=RESULT_FROM_CACHE)

    def test_invalid_currency(self):
        self._set_request_post_return_value()
        self._assert_result(currency='BITCOIN', expected_result='Currency not found: BITCOIN')

    def test_get_exchange_of_amount(self):
        self._set_request_post_return_value()
        result = self.mnb.get_exchange_of_amount('EUR', '2')
        self.assertEqual('MNB exchange rate of  2 EUR = 1000,00 HUF  (2018-01-03)', result)

    def test_get_exchange_of_float_amount(self):
        self._set_request_post_return_value()
        result = self.mnb.get_exchange_of_amount('EUR', '2.5')
        self.assertEqual('MNB exchange rate of  2.5 EUR = 1250,00 HUF  (2018-01-03)', result)

    def test_get_exchange_of_amount_with_error(self):
        self._set_request_post_return_value(code=404, content='dummy')
        result = self.mnb.get_exchange_of_amount('EUR', '2')
        self.assertEqual('Server response: 404', result)
