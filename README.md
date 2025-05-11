# onenote-dump

A utility for converting a Microsoft OneNote notebook to markdown, with a clean architecture design for better extensibility.

## Features

- Convert OneNote notebooks to markdown format
- Compatible with [Notable](https://github.com/notable/notable)
  - Markdown with metadata headers
  - `@attachment` syntax for attachments
  - `@note` syntax for note links
- Microsoft Graph API integration
- Concurrent processing with pipeline architecture
- Type-safe with full type hints
- Both CLI and programmatic usage

## Project Structure

```
onenote_dump/
├── core.py         # Core API operations
├── interactor.py   # High-level interface
├── main.py         # CLI entry point
├── onenote.py      # OneNote API client
├── onenote_auth.py # Authentication
└── pipeline.py     # Concurrent processing
```

## Architecture

```mermaid
graph TD
    A[CLI / Client Code] --> B[OneNoteInteractor]
    B --> C[OneNoteCore]
    C --> D[Microsoft Graph API]
    B --> E[Pipeline]
    E --> F[Page Processor]
    F --> G[Markdown Converter]
    G --> H[File System]
```

### Components

- **OneNoteInteractor**: 高级接口层，提供友好的API
  - 处理参数验证和类型转换
  - 提供直观的方法名和参数
  - 返回结构化的结果

- **OneNoteCore**: 核心API操作层
  - 处理与Microsoft Graph API的通信
  - 管理认证和会话
  - 提供底层API调用

- **Pipeline**: 并发处理层
  - 使用线程池处理页面转换
  - 实现异步IO操作
  - 管理资源和错误处理

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Interactor
    participant Core
    participant API
    participant Pipeline
    participant FileSystem

    User->>Interactor: dump_notebook()
    Interactor->>Core: get_notebooks()
    Core->>API: HTTP Request
    API-->>Core: Notebook Data
    Core-->>Interactor: Notebook Info
    Interactor->>Core: get_notebook_pages()
    Core->>API: HTTP Request
    API-->>Core: Page Data
    Core-->>Interactor: Page Info
    Interactor->>Pipeline: add_page()
    Pipeline->>API: Get Content
    API-->>Pipeline: Page Content
    Pipeline->>FileSystem: Save as Markdown
    FileSystem-->>User: Done
```

## Installation

### Requirements
- Python 3.6+
- Microsoft Account with OneNote access

### Using pip

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the environment:
```bash
# On Windows
.venv\Scripts\activate.bat

# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
# For basic usage
pip install -r requirements.txt

# For development (includes type hints)
pip install -r requirements.txt -r requirements-dev.txt
```

### Using Poetry

```bash
poetry install
```

## Usage

### Command Line Interface

```bash
# Basic usage
python -m onenote_dump.main <notebook> <output directory>

# Example: dump specific notebook
python -m onenote_dump.main "Work Notes" ./output

# Example: dump specific section with verbose output
python -m onenote_dump.main "Work Notes" ./output --section "Projects" -v

# Example: limit number of pages
python -m onenote_dump.main "Work Notes" ./output -m 10

# Example: start from specific page
python -m onenote_dump.main "Work Notes" ./output -s 5
```

### As a Library

```python
from onenote_dump.interactor import OneNoteInteractor

# Initialize the interactor
interactor = OneNoteInteractor(verbose=True)

# List all notebooks
notebooks = interactor.list_notebooks()
for notebook in notebooks:
    print(f"Found notebook: {notebook['displayName']}")

# Dump a specific notebook
result = interactor.dump_notebook(
    notebook_name="Work Notes",
    output_dir="./output",
    section_name="Projects",  # Optional: specific section
    max_pages=100,          # Optional: limit pages
    start_page=1,           # Optional: start page
    new_session=False       # Optional: force new auth session
)

# Check results
print(f"Exported {result['total_pages']} pages in {result['duration_seconds']:.1f} seconds")
print(f"Output directory: {result['output_path']}")
```

### Poetry Users

If you're using Poetry, you can use the `onenote-dump` binary:
created with `poetry install` instead of `python onenote_dump/main.py`.

For full usage details:

```
onenote-dump --help
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

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/istarwyh/onenote-dump.git
cd onenote-dump

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate.bat on Windows

# Install dependencies including development tools
pip install -r requirements.txt -r requirements-dev.txt
```

### Project Design

1. **Clean Architecture**
   - Separation of concerns with clear layers
   - Dependency injection for better testability
   - Clear boundaries between components

2. **Type Safety**
   - Full type hints coverage
   - Mypy for static type checking
   - Runtime type validation

3. **Concurrent Processing**
   - Thread pool for IO operations
   - Pipeline pattern for data processing
   - Resource management

4. **Error Handling**
   - Structured error types
   - Graceful degradation
   - Detailed error messages

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

#### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `docs`: Documentation only changes
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat: add notebook search functionality
fix: handle API rate limiting correctly
docs: update installation instructions
```
