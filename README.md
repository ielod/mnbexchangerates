MNB Exchange Rates CLI
======================

This python package provides a CLI for getting actual available MNB
exchange rates. The exchange rates are fetched from MNB via their SOAP API.

MNB announces its new daily rates some time after 11:00, on every weekday.


Installation
------------

To install use e.g. pip:

> python -m pip install .

This will install the CLI.


Usage of CLI
------------

To query exchange rates for a currency:

> mnb-exc-rate < currency >

e.g.:

> mnb-exchange-rate eur

For usage help, see:

> mnb-exchange-rate -h

For debug log:

> mnb-exchange-rate eur --debug

For calcuting an amount with the actual exchange rate:

> mnb-exchange-rate usd --amount 25

Code check
----------

For code style check with pylint and flake8 and for unittest with py38 and py310:
run 'tox' in the root of the repository.
