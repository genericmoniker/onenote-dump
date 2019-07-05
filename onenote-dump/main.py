import json
import logging
import os
import pathlib

import log
import onenote_auth
import onenote
import pipeline


def main():
    log.setup_logging(logging.DEBUG)

    # Allow a redirect URI over plain HTTP (no TLS):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    # Authorize the app:
    s = onenote_auth.get_session()

    notebook = 'Software Development'

    out_dir = pathlib.Path(r'D:\Temp\Notable')
    out_dir.mkdir(parents=True, exist_ok=True)
    pipe = pipeline.Pipeline(s, notebook, out_dir)

    pc = 0
    for page in onenote.get_notebook_pages(s, notebook):
        pipe.add_page(page)
        pc += 1
        if pc > 3:
            break

    pipe.done()


main()
