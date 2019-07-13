import argparse
import logging
import os
import pathlib
import time

import log
import onenote_auth
import onenote
import pipeline

logger = logging.getLogger()


def main():
    args = parse_args()
    if args.verbose:
        log.setup_logging(logging.DEBUG)
    else:
        log.setup_logging(logging.INFO)

    # Allow a redirect URI over plain HTTP (no TLS):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    # Authorize the app:
    s = onenote_auth.get_session()

    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info('Writing to "%s"', output_dir)

    start_time = time.perf_counter()
    pipe = pipeline.Pipeline(s, args.notebook, output_dir)
    for page_count, page in enumerate(
        onenote.get_notebook_pages(s, args.notebook), 1
    ):
        logger.info('Page: %s', page['title'])
        pipe.add_page(page)
        if args.max_pages and page_count > args.max_pages:
            break

    pipe.done()
    stop_time = time.perf_counter()
    logger.info('Done!')
    logger.info('%s pages in %.1f seconds', page_count, stop_time - start_time)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('notebook', help='display name of notebook to dump')
    parser.add_argument('output_dir', help='directory to which to output')
    parser.add_argument('-m', '--max-pages', type=int, help='max pages to dump')
    parser.add_argument('-v', '--verbose', action="store_true", help='show verbose output')
    return parser.parse_args()


main()
