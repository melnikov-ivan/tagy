# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tagy is a Python static site generator. The entire core is a single file (`tagy.py`, ~400 lines) that converts Markdown/HTML content with YAML frontmatter into static HTML using Jinja2 templates.

## Development Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/Pagination_test.py -v

# Run a specific test
python -m pytest tests/Pagination_test.py -k "test_name" -v
```

## Building & Publishing

```bash
rm dist/*
pip install setuptools
python setup.py sdist
twine upload dist/*
```

## Architecture

**Single-file core** — `tagy.py` contains all logic:
- `generate()` — main entry point, loads site config + content, renders all pages
- `load_site()` → `load_config()` → `load_content()` — reads `config.yaml` and content directory, builds indexes (tags, categories, etc.)
- `generate_site()` → `generate_page()` / `generate_index()` — renders Jinja2 templates to HTML output
- `serve(port)` + `watch()` — dev server with file-change auto-rebuild

**Content model** — pages are Markdown/HTML files with YAML frontmatter, parsed by `load_page()`. Indexes group pages by custom fields (tags, categories). Pagination is handled via a `paginate()` Jinja2 global that queues additional pages.

**Custom Jinja2 extensions** — `where` filter (query pages), `breadcrumbs` filter, `thumb` filter (image thumbnails via Pillow), `equalto` test.

## Dependencies

- Jinja2 3.1 (templating), PyYAML (config/frontmatter), mistune 0.8.1 (Markdown), Pillow (thumbnails)
