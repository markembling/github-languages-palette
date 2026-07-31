LINGUIST_LANGS_PATH := "lib/linguist/languages.yml"
LINGUIST_POPULAR_PATH := "lib/linguist/popular.yml"
LINGUIST_REPO_MAIN_URL := "https://raw.githubusercontent.com/github-linguist/linguist/main"

# Invoke the generator with no additional args
run *args:
    .venv/bin/python -m generator {{args}}

# Generate all palettes, tracking Linguist's main branch by default
all *args: clean
    #!/usr/bin/env bash
    set -euo pipefail
    just _generate-all "{{LINGUIST_REPO_MAIN_URL}}/{{LINGUIST_LANGS_PATH}}" "{{LINGUIST_REPO_MAIN_URL}}/{{LINGUIST_POPULAR_PATH}}" {{args}}

# Generate all palettes pinned to Linguist's latest tagged release
all-release *args: clean
    #!/usr/bin/env bash
    set -euo pipefail
    urls=($(.venv/bin/python scripts/resolve_release_url.py github-linguist/linguist \
        {{LINGUIST_LANGS_PATH}} {{LINGUIST_POPULAR_PATH}}))
    just _generate-all "${urls[0]}" "${urls[1]}" {{args}}

# Internal: fetch languages/popular data once, then generate every format from the local copies
_generate-all languages_url popular_url *extra_args:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p palettes
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    curl -sfL "{{languages_url}}" -o "$tmp/languages.yml"
    curl -sfL "{{popular_url}}" -o "$tmp/popular.yml"
    for fmt in ccxml gpl ase aco json csv; do
        .venv/bin/python -m generator --format "$fmt" "palettes/githublangs.$fmt" \
            --languages-file "$tmp/languages.yml" --popular-file "$tmp/popular.yml" {{extra_args}}
    done

# Remove existing palettes
clean:
    rm -rf palettes/*

# Set up the virtual environment and install dependencies
bootstrap:
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
