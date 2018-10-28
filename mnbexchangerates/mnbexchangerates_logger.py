import logging


DEBUG = logging.DEBUG
INFO = logging.INFO


class MNBExchangeRatesLogger:

    def __init__(self, debug=False):
        self.logger = None
        if debug:
            self.log_level = DEBUG
        else:
            self.log_level = INFO

    def get_logger(self):
        self.logger = logging.getLogger('mnb-exchange-rates')
        if not self.logger.handlers:
            self.init_logger()
        return self.logger

    def init_logger(self):
        self.logger.setLevel(self.log_level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
