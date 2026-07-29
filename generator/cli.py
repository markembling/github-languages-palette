import argparse
from pathlib import Path
from typing import Sequence

from .sources import LINGUIST_LANGS_URL, LINGUIST_POPULAR_URL
from .generate import generate_palette


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Creates a palette file for GitHub language colours.",
                                     epilog="Mark Embling (markembling.info)")
    parser.add_argument("output", help="output filename")
    parser.add_argument("--format", help="palette format (default: ccxml)", 
                                    default="ccxml",
                                    choices=["ccxml", "gpl", "ase", "aco", "json", "csv"])
    
    languages_group = parser.add_mutually_exclusive_group()
    languages_group.add_argument("--languages-url",
                                 help="URL for languages YAML (default: URL for languages.yml file on GitHub)", 
                                 default=LINGUIST_LANGS_URL)
    languages_group.add_argument("--languages-file",
                                 help="local file for languages YAML (default: none)",
                                 default=None)
    
    popular_group = parser.add_mutually_exclusive_group()
    popular_group.add_argument("--popular-url",
                               help="URL for popular languages YAML (default: URL for popular.yml file on GitHub)",
                               default=LINGUIST_POPULAR_URL)
    popular_group.add_argument("--popular-file",
                               help="local file for popular languages YAML (default: none)",
                               default=None)
    parser.add_argument("--no-popular-first", action="store_true", help="prevent ordering with popular languages first")
    
    return parser


def run(argv: Sequence[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        generate_palette(
            output=Path(args.output),
            format=args.format,
            languages_url=args.languages_url,
            popular_url=args.popular_url,
            popular_sort=not args.no_popular_first,
            languages_file=Path(args.languages_file) if args.languages_file else None,
            popular_file=Path(args.popular_file) if args.popular_file else None
        )
        print(f"✓ {Path(args.output)}")
    except Exception as e:
        print(f"✗ {Path(args.output)}: {e}")
        return 1

    return 0
