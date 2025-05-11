import argparse
import logging
import os
import pathlib
import time

from onenote_dump import log, onenote, onenote_auth, pipeline

logger = logging.getLogger()


def main():
    args = parse_args()
    
    # Allow a redirect URI over plain HTTP (no TLS):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    # No warning if scope is more than asked for:
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    interactor = onenote.OneNoteInteractor(verbose=args.verbose)
    
    try:
        result = interactor.dump_notebook(
            notebook_name=args.notebook,
            output_dir=args.output_dir,
            section_name=args.section,
            max_pages=args.max_pages,
            start_page=args.start_page,
            new_session=args.new_session
        )
        
        logger.info("Done!")
        logger.info("%s pages in %.1f seconds", 
                   result["total_pages"], 
                   result["duration_seconds"])
    except onenote.NotebookNotFound as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


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
