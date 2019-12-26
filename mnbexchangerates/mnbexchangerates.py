import html
import xml.etree.ElementTree as ET

import requests

from mnbexchangerates import mnbexchangerates_cache
from mnbexchangerates import mnbexchangerates_logger


URL = 'http://www.mnb.hu/arfolyamok.asmx?wsdl'
HEADERS = {'content-type': 'application/soap+xml'}
BODY = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
  xmlns:ns0="http://www.mnb.hu/"
  xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header/>
    <ns1:Body><ns0:GetCurrentExchangeRates/></ns1:Body>
</SOAP-ENV:Envelope>"""


class MNBExchangeRates:

    def __init__(self, debug=False, cache_only=False):
        self.log = mnbexchangerates_logger.MNBExchangeRatesLogger(debug=debug).get_logger()
        self.log.debug('ON')
        self.cache = mnbexchangerates_cache.MNBExchangeRateCache(debug=debug, cache_only=cache_only)

    def _parse_soap_xml(self, xml_content):
        unescaped = html.unescape(xml_content.decode())
        self.log.debug('Unescaped xml content: %s', unescaped)
        try:
            root = ET.fromstring(unescaped)
        except ET.ParseError as exc:
            self.log.debug('Parse error: %s', str(exc))
            return None

        day_list = root.findall(".//{http://www.mnb.hu/webservices/}Day")
        rates = root.findall(".//{http://www.mnb.hu/webservices/}Rate")

        if day_list and rates:
            return {'date': day_list[0].attrib['date'],
                    'rates': [(rate.attrib['unit'], rate.attrib['curr'], rate.text) for rate in rates]}
        return None

    @classmethod
    def _simplified_number_format(cls, number):
        number = str(number).replace('.', ',')
        if ',' in number:
            while number[-1] == '0':
                number = number[:-1]
            if number[-1] == ',':
                number = number[:-1]
        return number

    def fetch_rates(self):
        response = requests.post(URL, data=BODY, headers=HEADERS)
        self.log.debug('Response from url %s : %s -- %s', URL, response.status_code, response.content)
        if response.status_code == 200:
            rates = self._parse_soap_xml(response.content)
            if rates:
                self.cache.save(rates)
                return rates
            self.log.debug('Exchange rates parsing failed. Invalid content?')
            raise Exception('Malformed content received from server')
        raise Exception('Server response: %s' % response.status_code)

    def get_rates(self):
        cached_rates = self.cache.load()
        if cached_rates is None:
            self.log.debug('Cache is empty, so fetching now...')
            return self.fetch_rates()
        return cached_rates

    def get_rate_for_currency(self, currency):
        rates_dict = self.get_rates()
        rate = [r for r in rates_dict['rates'] if currency in r]
        self.log.debug('Found rate: %s', rate)
        if rate:
            return {'date': rates_dict['date'],
                    'unit': rate[0][0],
                    'currency': rate[0][1],
                    'rate': rate[0][2]}
        raise Exception('Currency not found: %s' % currency)

    def get_str_of_rate_for_currency(self, currency):
        currency = currency.upper()
        self.log.debug('Currency to look for: %s', currency)
        try:
            rate_dict = self.get_rate_for_currency(currency)
            answer = 'MNB exchange rate of  %s %s = %s HUF  (%s)' % (
                rate_dict['unit'],
                rate_dict['currency'],
                self._simplified_number_format(rate_dict['rate']),
                rate_dict['date'])
        except Exception as exc:  # pylint: disable=W0703
            answer = str(exc)
            self.log.debug(answer)
        return answer

    def get_exchange_of_amount(self, currency, amount):
        currency = currency.upper()
        self.log.debug('Currency to look for: %s', currency)
        self.log.debug('Requested amount: %s', amount)
        try:
            rate_dict = self.get_rate_for_currency(currency)
            total = (float(amount) * float(rate_dict['rate'].replace(',', '.'))) / float(rate_dict['unit'])
            total = self._simplified_number_format("%.2f" % total)
            answer = 'MNB exchange rate of  %s %s = %s HUF  (%s)' % (
                self._simplified_number_format(amount),
                rate_dict['currency'],
                total,
                rate_dict['date'])
        except Exception as exc:  # pylint: disable=W0703
            answer = str(exc)
            self.log.debug(answer)
        return answer
