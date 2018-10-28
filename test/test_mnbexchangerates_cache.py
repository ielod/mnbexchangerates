from datetime import datetime

import mock
import unittest

from mnbexchangerates import mnbexchangerates_cache as cache


CACHE_VALID = {'date': '2018-01-03', 'rates': [('1', 'EUR', '600,000')]}
CACHE_OLD = {'date': '2017-12-01', 'rates': [('1', 'EUR', '200,000')]}
CACHE_YESTERDAY = {'date': '2018-01-02', 'rates': [('1', 'EUR', '300,000')]}
CACHE_FROM_FRIDAY = {'date': '2018-07-06', 'rates': [('1', 'EUR', '400,000')]}
CACHE_INVALID = None


class MNBExchangeRateCacheTest(unittest.TestCase):

    def setUp(self):
        self.patch_open = mock.patch('mnbexchangerates.mnbexchangerates_cache.open')
        self.mock_open = self.patch_open.start()
        self.patch_datetime = mock.patch('mnbexchangerates.mnbexchangerates_cache.datetime')
        self.mock_datetime = self.patch_datetime.start()
        self.patch_pickle = mock.patch('mnbexchangerates.mnbexchangerates_cache.pickle')
        self.mock_pickle = self.patch_pickle.start()
        self.patch_os = mock.patch('mnbexchangerates.mnbexchangerates_cache.os')
        self.mock_os = self.patch_os.start()
        self.mock_datetime.now.return_value = datetime(2018, 1, 3, 14, 0)
        self.cache = cache.MNBExchangeRateCache(True)

    def tearDown(self):
        self.patch_open.stop()
        self.patch_datetime.stop()
        self.patch_pickle.stop()
        self.patch_os.stop()
        self.mnb = None

    def test_valid_cache(self):
        self.mock_pickle.load.return_value = CACHE_VALID
        self.assertEqual(CACHE_VALID, self.cache.load())

    def test_invalid_cache(self):
        self.mock_pickle.load.return_value = 'invalid'
        self.assertEqual(CACHE_INVALID, self.cache.load())

    def test_empty_dict_in_cache(self):
        self.mock_pickle.load.return_value = {}
        self.assertEqual(CACHE_INVALID, self.cache.load())

    def test_invalid_dict_in_cache(self):
        self.mock_pickle.load.return_value = {'foo': 'bar'}
        self.assertEqual(CACHE_INVALID, self.cache.load())

    def test_cannot_unpickle(self):
        self.mock_pickle.load.side_effect = EOFError('dummy')
        self.assertEqual(CACHE_INVALID, self.cache.load())

    def test_old_cache(self):
        self.mock_pickle.load.return_value = CACHE_OLD
        self.assertEqual(CACHE_INVALID, self.cache.load())

    def test_cache_from_yesterday_but_its_too_early(self):
        self.mock_datetime.now.return_value = datetime(2018, 1, 3, 9, 0)
        self.mock_pickle.load.return_value = CACHE_YESTERDAY
        self.assertEqual(CACHE_YESTERDAY, self.cache.load())

    def test_cahce_old_but_weekend(self):
        self.mock_datetime.now.return_value = datetime(2018, 7, 7, 18, 0)
        self.mock_datetime.strptime.return_value = datetime(2018, 7, 6)
        self.mock_pickle.load.return_value = CACHE_FROM_FRIDAY
        self.assertEqual(CACHE_FROM_FRIDAY, self.cache.load())

    def test_cahce_from_friday_but_early_monday_morning(self):
        self.mock_datetime.now.return_value = datetime(2018, 7, 9, 10, 0)
        self.mock_datetime.strptime.return_value = datetime(2018, 7, 6)
        self.mock_pickle.load.return_value = CACHE_FROM_FRIDAY
        self.assertEqual(CACHE_FROM_FRIDAY, self.cache.load())

    def test_cahce_from_friday_and_monday_afternoon(self):
        self.mock_datetime.now.return_value = datetime(2018, 7, 9, 14, 0)
        self.mock_datetime.strptime.return_value = datetime(2018, 7, 6)
        self.mock_pickle.load.return_value = CACHE_FROM_FRIDAY
        self.assertEqual(CACHE_INVALID, self.cache.load())

    def test_write_cache(self):
        self.cache.save({})

    def test_write_cache_error(self):
        self.mock_open.side_effect = IOError('dummy')
        self.cache.save({})

    def test_ensure_cache_dir(self):
        self.mock_os.path.isdir.return_value = False
        self.cache._ensure_cache_dir()

    def test_ensure_cache_dir_error(self):
        self.mock_os.path.isdir.return_value = False
        self.mock_os.makedirs.side_effect = IOError('dummy')
        self.cache._ensure_cache_dir()
