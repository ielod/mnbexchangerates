from datetime import datetime
from datetime import timedelta
import os
import pickle

from mnbexchangerates import mnbexchangerates_logger


RATES_CACHE_DIR = '~/.config/mnbexchangerates'
RATES_CACHE_FILE = RATES_CACHE_DIR + '/exchange_rates.cache'
DATE_FORMAT = '%Y-%m-%d'
REFRESH_HOUR = 11


class MNBExchangeRateCache:

    def __init__(self, debug=False, cache_only=False):
        self.log = mnbexchangerates_logger.MNBExchangeRatesLogger(debug).get_logger()
        self.log.debug('Cache file path: %s', RATES_CACHE_FILE)
        self._ensure_cache_dir()
        self.cache_only = cache_only
        self.time = None
        self.today = None
        self.yesterday = None

    def _ensure_cache_dir(self):
        if not os.path.isdir(os.path.expanduser(RATES_CACHE_DIR)):
            try:
                os.makedirs(os.path.expanduser(RATES_CACHE_DIR))
                self.log.debug('Cache directory created (%s)', RATES_CACHE_DIR)
            except IOError:
                self.log.debug('Could not create cache directory (%s)', RATES_CACHE_DIR)

    def _read_cache(self):
        try:
            with open(os.path.expanduser(RATES_CACHE_FILE), 'rb') as cache:
                data = pickle.load(cache)
                self.log.debug('Cache file found. Read rates: %s', data)
        except (IOError, EOFError, KeyError) as exc:
            self.log.debug('Error when reading cache file. Invalidating read cache. (%s: %s)',
                           type(exc).__name__,
                           exc.args)
            data = None
        return data

    def save(self, rates):
        self.log.debug('Writing rates to cache file. (Rates: %s)', rates)
        try:
            with open(os.path.expanduser(RATES_CACHE_FILE), 'wb') as cache:
                pickle.dump(rates, cache, pickle.HIGHEST_PROTOCOL)
                self.log.debug('Cache file stored.')
        except IOError as exc:
            self.log.debug('Error while writing cache file (%s)', str(exc))

    def _refresh_date(self):
        self.time = datetime.now()
        self.today = self.time.strftime(DATE_FORMAT)
        self.yesterday = (self.time - timedelta(1)).strftime(DATE_FORMAT)
        self.log.debug('Date: %s - Hour: %s', self.today, self.time.hour)

    def _check_not_weekend(self, cache_date):
        cache_date = datetime.strptime(cache_date, DATE_FORMAT)
        self.log.debug('Parsed cache date: %s', cache_date)
        return not ((self.time.weekday() == 5 and
                     (cache_date + timedelta(1)).strftime(DATE_FORMAT) == self.today) or
                    (self.time.weekday() == 6 and
                     (cache_date + timedelta(2)).strftime(DATE_FORMAT) == self.today) or
                    (self.time.weekday() == 0 and self.time.hour < REFRESH_HOUR and
                     (cache_date + timedelta(3)).strftime(DATE_FORMAT) == self.today))

    def load(self):
        self._refresh_date()
        cached_rates = self._read_cache()
        if cached_rates is not None:
            if (not isinstance(cached_rates, dict) or
                    cached_rates.get('date') is None or
                    cached_rates.get('rates') is None):
                self.log.debug('Cache seem to be invalid, emptying it.')
                cached_rates = None
            elif self.cache_only:
                self.log.debug('Forced use of cache.')
            elif (cached_rates['date'] != self.today and
                  not (cached_rates['date'] == self.yesterday and self.time.hour < REFRESH_HOUR) and
                  self._check_not_weekend(cached_rates['date'])):
                self.log.debug('Cache is old, emptying it.')
                cached_rates = None
            else:
                self.log.debug('Cache is up to date.')
        return cached_rates
