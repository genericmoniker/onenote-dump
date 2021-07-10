import logging
import sys

SIMPLE = '%(message)s'
VERBOSE = '%(asctime)s %(levelname)1.1s %(message)s'


def setup_logging(level):
    fmt = VERBOSE if level == logging.DEBUG else SIMPLE
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(fmt))
    handler.setLevel(level)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)
