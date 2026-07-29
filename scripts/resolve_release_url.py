#!/usr/bin/env python3
"""
Resolves raw URLs for files in a repo, as of its latest release.
"""

import argparse
import json
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def get_latest_release_tag(repo: str) -> str:
    request = Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers={"Accept": "application/vnd.github+json"},
    )
    with urlopen(request) as response:
        return json.load(response)["tag_name"]


def build_raw_url(repo: str, tag: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{tag}/{path}"


def path_exists(repo: str, tag: str, path: str) -> bool:
    request = Request(build_raw_url(repo, tag, path), method="HEAD")
    try:
        with urlopen(request):
            return True
    except HTTPError as e:
        if e.code == 404:
            return False
        raise


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="owner/repo, e.g. github-linguist/linguist")
    parser.add_argument("paths", nargs="+", help="one or more paths within the repo")
    args = parser.parse_args(argv)

    try:
        tag = get_latest_release_tag(args.repo)
    except Exception as e:
        print(f"error: could not resolve latest release for {args.repo}: {e}", file=sys.stderr)
        return 1

    try:
        missing = [path for path in args.paths if not path_exists(args.repo, tag, path)]
    except Exception as e:
        print(f"error: could not verify paths against {args.repo} at {tag}: {e}", file=sys.stderr)
        return 1

    if missing:
        for path in missing:
            print(f"error: {path!r} does not exist in {args.repo} at {tag}", file=sys.stderr)
        return 1

    for path in args.paths:
        print(build_raw_url(args.repo, tag, path))
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
