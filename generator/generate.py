from pathlib import Path

from .sources import (
    get_linguist_language_colours,
    get_linguist_popular_languages,
    load_linguist_language_colours,
    load_linguist_popular_languages,
    order_language_colours
)
from .generators import generator_for_format


def generate_palette(
    output: Path,
    format: str,
    languages_url: str,
    popular_url: str,
    languages_file: Path | None = None,
    popular_file: Path | None = None,
) -> None:

    # Load the linguist language colours from file or URL
    if languages_file is not None:
        linguist_data = load_linguist_language_colours(languages_file)
    else:
        linguist_data = get_linguist_language_colours(languages_url)

    # Load the popular languages list from file or URL
    if popular_file is not None:
        popular_languages = load_linguist_popular_languages(popular_file)
    else:
        popular_languages = get_linguist_popular_languages(popular_url)

    # Create the final ordered dictionary of colours
    final_data = order_language_colours(linguist_data, popular_languages)

    # Create the appropriate generator and generate the palette file
    generator = generator_for_format(format)
    generator.generate_file(final_data, output)
