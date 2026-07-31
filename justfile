# Invoke the generator with no additional args
run *args:
    .venv/bin/python -m generator {{args}}

# Generate all palettes, tracking Linguist's main branch by default
all *args: clean
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p palettes
    for fmt in ccxml gpl ase aco json csv; do
        .venv/bin/python -m generator --format "$fmt" "palettes/githublangs.$fmt" {{args}}
    done

# Generate all palettes pinned to Linguist's latest tagged release
all-release:
    #!/usr/bin/env bash
    set -euo pipefail
    urls=($(.venv/bin/python scripts/resolve_release_url.py github-linguist/linguist \
        lib/linguist/languages.yml lib/linguist/popular.yml))
    just all --languages-url "${urls[0]}" --popular-url "${urls[1]}"

# Remove existing palettes
clean:
    rm -rf palettes/*

# Set up the virtual environment and install dependencies
bootstrap:
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
