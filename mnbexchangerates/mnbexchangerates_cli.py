from __future__ import print_function
import argparse
import sys

from mnbexchangerates import mnbexchangerates


def parse_arguments():
    parser = argparse.ArgumentParser(description='Fetch MNB Exchange Rates')
    parser.add_argument('currency', help='Fetch Exchange rate from <currency> to HUF')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-a', '--amount', type=int)
    return parser.parse_args()


def main():
    args = parse_arguments()
    mnb_exchange_rate = mnbexchangerates.MNBExchangeRates(args.debug)
    if args.amount:
        print(mnb_exchange_rate.get_exchange_of_amount(args.currency, args.amount))
    else:
        print(mnb_exchange_rate.get_str_of_rate_for_currency(args.currency))


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())