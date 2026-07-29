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
    popular_sort: bool = True,
    languages_file: Path | None = None,
    popular_file: Path | None = None,
) -> None:

    # Load the linguist language colours from file or URL
    if languages_file is not None:
        linguist_data = load_linguist_language_colours(languages_file)
    else:
        linguist_data = get_linguist_language_colours(languages_url)


    # If required, load the popular languages list from file or URL and order
    # the linguist data accordingly.
    if popular_sort:
        if popular_file is not None:
            popular_languages = load_linguist_popular_languages(popular_file)
        else:
            popular_languages = get_linguist_popular_languages(popular_url)
        linguist_data = order_language_colours(linguist_data, popular_languages)

    # Create the appropriate generator and generate the palette file
    generator = generator_for_format(format)
    generator.generate_file(linguist_data, output)
