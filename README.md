# onenote-dump

A utility for converting a Microsoft OneNote notebook to markdown.

The output is targeted for compatibility with
[Notable](https://github.com/notable/notable), which means:

* Markdown has metadata at the beginning
* Links to attachments use `@attachment` syntax
* Links to other notes use `@note` syntax

It retrieves OneNote data through the Microsoft graph API, so the notebook
needs to be synchronized with the cloud.

## Installation

The script requires Python 3.6+.

You'll probably want a virtual environment:

```
python -m venv .venv
```

Then activate the virtual environment, and install the dependencies. For
example:

```
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

If you have poetry, you can use that instead:

```
poetry install
```

## Running

```
python onenote_dump/main.py <notebook> <output directory>
```

The `<notebook>` parameter is the display name of the notebook. For example:

```
python onenote_dump/main.py "Software Development Notes" C:\Temp\dump
```

NOTE: If you are using poetry, you can use the `onenote-dump` binary that is
created with `poetry install` instead of `python onenote_dump/main.py`.

For full usage details:

```
python onenote_dump/main.py --help
```

When run, the script will launch a browser window so that you can authorize the
script to access your OneNote data. Subsequent runs won't require this, so long
as the authorization token is good (about an hour). If you want to force
re-authentication, you can pass the "--new-session" param.

The output directory and parents will be created if needed.

If your notebook is large, there is a good chance you'll hit the request rate
limit on Microsoft's API, which will cause the script to wait for a few minutes
and try again. You may wish to kill the program (Ctrl+C) and use the
`--start-page` option some time later, or the `--section` option to select a
subset of a notebook.

If you're happy with the output, you can copy it to your Notable notes
directory.
