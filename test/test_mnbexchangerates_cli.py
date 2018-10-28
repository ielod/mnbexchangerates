import mock
import unittest

from mnbexchangerates import mnbexchangerates_cli


class TestMenuCLI(unittest.TestCase):

    def setUp(self):
        self.patch_argparser = mock.patch("mnbexchangerates.mnbexchangerates_cli.argparse.ArgumentParser")
        self.mock_argparser = self.patch_argparser.start()
        self.patch_mnb = mock.patch("mnbexchangerates.mnbexchangerates.MNBExchangeRates")
        self.mock_mnb = self.patch_mnb.start()

    def tearDown(self):
        self.patch_argparser.stop()
        self.patch_mnb.stop()

    def _set_amount(self, amount):
        args_mock = mock.MagicMock()
        args_mock.amount = amount
        self.mock_argparser.return_value.parse_args.return_value = args_mock

    def test_cli_without_amount(self):
        self._set_amount(None)
        self.assertEqual(None, mnbexchangerates_cli.main())

    def test_cli_with_amount(self):
        self._set_amount(1)
        self.assertEqual(None, mnbexchangerates_cli.main())
