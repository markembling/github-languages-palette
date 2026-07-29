# Invoke the generator with no additional args
run *args:
    .venv/bin/python -m generator {{args}}

# Generate all palettes
all *args: clean
    mkdir -p palettes
    for FMT in ccxml gpl ase aco json csv; do \
        .venv/bin/python -m generator --format $FMT palettes/githublangs.$FMT {{args}}; \
    done

# Remove existing palettes
clean:
    rm -rf palettes/*

# Set up the virtual environment and install dependencies
bootstrap:
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
