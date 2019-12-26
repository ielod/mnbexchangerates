import mock
import unittest

import argparse

from mnbexchangerates import mnbexchangerates_cli


class TestMenuCLI(unittest.TestCase):

    def setUp(self):
        self.patch_argparser = mock.patch("mnbexchangerates.mnbexchangerates_cli.argparse.ArgumentParser")
        self.mock_argparser = self.patch_argparser.start()
        self.patch_mnb = mock.patch("mnbexchangerates.mnbexchangerates.MNBExchangeRates")
        self.mock_mnb = self.patch_mnb.start()
        self.mock_rates = mock.MagicMock()
        self.mock_mnb.return_value = self.mock_rates

    def tearDown(self):
        self.patch_argparser.stop()
        self.patch_mnb.stop()

    def _set_amount(self, amount):
        args_mock = mock.MagicMock()
        args_mock.amount = None if amount is None else mnbexchangerates_cli.supported_float(amount)
        self.mock_argparser.return_value.parse_args.return_value = args_mock

    def test_cli_without_amount(self):
        self._set_amount(None)
        self.assertEqual(None, mnbexchangerates_cli.main())
        self.mock_rates.get_str_of_rate_for_currency.assert_called_with(mock.ANY)
        self.mock_rates.get_exchange_of_amount.assert_not_called()

    def test_cli_with_amount(self):
        self._set_amount('1')
        self.assertEqual(None, mnbexchangerates_cli.main())
        self.mock_rates.get_exchange_of_amount.assert_called_with(mock.ANY, 1)
        self.mock_rates.get_str_of_rate_for_currency.assert_not_called()

    def test_cli_with_float_amount(self):
        self._set_amount('2.5')
        self.assertEqual(None, mnbexchangerates_cli.main())
        self.mock_rates.get_exchange_of_amount.assert_called_with(mock.ANY, 2.5)
        self.mock_rates.get_str_of_rate_for_currency.assert_not_called()

    def test_cli_with_comma_separated_float_amount(self):
        self._set_amount('2,5')
        self.assertEqual(None, mnbexchangerates_cli.main())
        self.mock_rates.get_exchange_of_amount.assert_called_with(mock.ANY, 2.5)
        self.mock_rates.get_str_of_rate_for_currency.assert_not_called()

    def test_cli_amount_is_not_a_valid_number(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            mnbexchangerates_cli.supported_float('not_a_number')
