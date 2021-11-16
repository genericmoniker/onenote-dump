import argparse
import logging
import os
import pathlib
import time

from onenote_dump import log, onenote, onenote_auth, pipeline

logger = logging.getLogger()


def main():
    args = parse_args()
    if args.verbose:
        log.setup_logging(logging.DEBUG)
    else:
        log.setup_logging(logging.INFO)

    # Allow a redirect URI over plain HTTP (no TLS):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # No warning if scope is more than asked for:
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    # Authorize the app:
    s = onenote_auth.get_session(args.new_session)

    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info('Writing to "%s"', output_dir)

    start_time = time.perf_counter()
    pipe = pipeline.Pipeline(s, args.notebook, output_dir)
    pages = 0
    try:
        for page_count, page in enumerate(
            onenote.get_notebook_pages(s, args.notebook, args.section), 1
        ):
            log_msg = f'Page {page_count}: {page["title"]}'
            if args.start_page is None or page_count >= args.start_page:
                logger.info(log_msg)
                pipe.add_page(page)
                pages += 1
            else:
                logger.info(log_msg + " [skipped]")
            if args.max_pages and page_count > args.max_pages:
                break
    except onenote.NotebookNotFound as e:
        logger.error(str(e))

    pipe.done()
    stop_time = time.perf_counter()
    logger.info("Done!")
    logger.info("%s pages in %.1f seconds", pages, stop_time - start_time)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", help="display name of notebook to dump")
    parser.add_argument("output_dir", help="directory to which to output")
    parser.add_argument("--section", help="display name of section to dump")
    parser.add_argument("-m", "--max-pages", type=int, help="max pages to dump")
    parser.add_argument(
        "-s", "--start-page", type=int, help="start page number to dump"
    )
    parser.add_argument(
        "-n",
        "--new-session",
        action="store_true",
        help="ignore saved auth token",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show verbose output"
    )
    return parser.parse_args()


main()
