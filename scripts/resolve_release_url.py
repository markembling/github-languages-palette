#!/usr/bin/env python3
"""
Resolve raw.githubusercontent.com URLs for files in a repo, pinned to a specific
ref.
"""

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def get_latest_release_tag(repo: str) -> str:
    request = Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers={"Accept": "application/vnd.github+json"},
    )
    with urlopen(request) as response:
        return json.load(response)["tag_name"]


def get_branch_head_sha(repo: str, branch: str) -> str:
    request = Request(
        f"https://api.github.com/repos/{repo}/commits/{branch}",
        headers={"Accept": "application/vnd.github+json"},
    )
    with urlopen(request) as response:
        return json.load(response)["sha"]


def build_raw_url(repo: str, ref: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"


def path_exists(repo: str, ref: str, path: str) -> bool:
    request = Request(build_raw_url(repo, ref, path), method="HEAD")
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
    parser.add_argument("--branch", help="resolve against this branch's HEAD, instead of the latest release")
    args = parser.parse_args(argv)

    try:
        ref = get_branch_head_sha(args.repo, args.branch) if args.branch else get_latest_release_tag(args.repo)
    except Exception as e:
        kind = f"branch {args.branch!r}" if args.branch else "latest release"
        print(f"error: could not resolve {kind} for {args.repo}: {e}", file=sys.stderr)
        return 1

    try:
        missing = [path for path in args.paths if not path_exists(args.repo, ref, path)]
    except Exception as e:
        print(f"error: could not verify paths against {args.repo} at {ref}: {e}", file=sys.stderr)
        return 1

    if missing:
        for path in missing:
            print(f"error: {path!r} does not exist in {args.repo} at {ref}", file=sys.stderr)
        return 1

    print(f"ref={ref}")
    for path in args.paths:
        print(build_raw_url(args.repo, ref, path))
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
