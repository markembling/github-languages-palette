import urllib.request
from pathlib import Path

import yaml
from colour import Color


LINGUIST_LANGS_URL = "https://raw.githubusercontent.com/github-linguist/linguist/refs/heads/main/lib/linguist/languages.yml"
LINGUIST_POPULAR_URL = "https://raw.githubusercontent.com/github-linguist/linguist/refs/heads/main/lib/linguist/popular.yml"


def get_linguist_language_colours(langs_url: str) -> dict[str, Color]:
    """Fetches the languages YAML from GitHub and returns a dictionary of colour names and values"""
    with urllib.request.urlopen(langs_url) as response:
        raw = response.read()
        data = yaml.safe_load(raw)
        return data_to_color_dict(data)

def load_linguist_language_colours(langs_file: Path) -> dict[str, Color]:
    """Loads the languages YAML from a local file and returns a dictionary of colour names and values"""
    with open(langs_file, "r") as f:
        data = yaml.safe_load(f)
        return data_to_color_dict(data)


def get_linguist_popular_languages(popular_url: str) -> list[str]:
    """Fetches the popular languages YAML from GitHub and returns a list of language names"""
    with urllib.request.urlopen(popular_url) as response:
        raw = response.read()
        return yaml.safe_load(raw)

def load_linguist_popular_languages(popular_file: Path) -> list[str]:
    """Loads the popular languages YAML from a local file and returns a list of language names"""
    with open(popular_file, "r") as f:
        return yaml.safe_load(f)


def data_to_color_dict(data) -> dict[str, Color]:
    """Converts the raw deserialised YAML data into a sorted dictionary of colour names and values"""
    return {name: Color(data["color"]) for name, data in sorted(data.items(), key=lambda x: x[0].lower()) if "color" in data}


def order_language_colours(data: dict[str, Color], popular_langs: list[str]) -> dict[str, Color]:
    """Orders the colours ensuring that the popular languages are at the top of the list"""
    order_set = set(popular_langs)
    ordered_keys = [key for key in popular_langs if key in data]
    remaining_keys = sorted(key for key in data if key not in order_set)
    return {key: data[key] for key in [*ordered_keys, *remaining_keys]}
