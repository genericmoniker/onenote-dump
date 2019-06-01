import logging
import sys

FMT = '%(asctime)s %(levelname)1.1s %(message)s'


def setup_logging(level):
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(FMT))
    handler.setLevel(level)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)
