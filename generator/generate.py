import argparse
import struct
import json
import urllib.request
import xml.etree.ElementTree as ET
from typing import Protocol, BinaryIO, Sequence

import yaml
from colour import Color


LINGUIST_LANGS_URL = "https://raw.githubusercontent.com/github-linguist/linguist/refs/heads/main/lib/linguist/languages.yml"
LINGUIST_POPULAR_URL = "https://raw.githubusercontent.com/github-linguist/linguist/refs/heads/main/lib/linguist/popular.yml"


class PaletteGenerator(Protocol):
    def generate_file(self, colors: dict[str, Color], path: str) -> None: ...

class CcxmlGenerator:
    PALETTE_XML_NS = "http://markembling.info/xmlschema/colourchooser/palette/1"

    def generate_file(self, colors: dict[str, Color], path: str) -> None:
        el_palette = ET.Element(self._element_name_namespaced("palette"))

        for lang, col in colors.items():
            el_colour = self._create_colour_element(lang, col)
            el_palette.append(el_colour)

        tree = ET.ElementTree(el_palette)
        ET.indent(tree, space="    ")
        tree.write(path, xml_declaration=True,
                         encoding='utf-8',
                         method="xml",
                         default_namespace=self.PALETTE_XML_NS)

    def _element_name_namespaced(self, name: str) -> str:
        return "{{{0}}}{1}".format(self.PALETTE_XML_NS, name)
    
    def _create_colour_element(self, name: str, color: Color):
        rgb = tuple(int(c * 255) for c in  color.rgb)

        el_colour = ET.Element(self._element_name_namespaced("colour"))
        el_name = ET.SubElement(el_colour, self._element_name_namespaced("name"))
        el_r = ET.SubElement(el_colour, self._element_name_namespaced("r"))
        el_g = ET.SubElement(el_colour, self._element_name_namespaced("g"))
        el_b = ET.SubElement(el_colour, self._element_name_namespaced("b"))
        el_opacity = ET.SubElement(el_colour, self._element_name_namespaced("opacity"))

        el_name.text = name
        el_r.text = str(rgb[0])
        el_g.text = str(rgb[1])
        el_b.text = str(rgb[2])
        el_opacity.text = "100"

        return el_colour

class GplGenerator:
    def generate_file(self, colors: dict[str, Color], path: str) -> None:
        with open(path, "w", newline="\n") as f:
            f.write("GIMP Palette\n")
            f.write("# See https://github.com/markembling/github-languages-palette\n")
            for name, col in colors.items():
                rgb = tuple(int(c * 255) for c in  col.rgb)
                f.write(f"{self._pad_number(rgb[0])} {self._pad_number(rgb[1])} {self._pad_number(rgb[2])} {name}\n")

    def _pad_number(self, num: int):
        return str(num).rjust(3)

class AseGenerator:
    def generate_file(self, colors: dict[str, Color], path: str) -> None:
        with open(path, "wb") as f:
            f.write(b'\x41\x53\x45\x46')  # Signature
            f.write(b'\x00\x01\x00\x00')  # Version

            # Number of blocks (colours + 2)
            f.write((len(colors) + 2).to_bytes(4, byteorder='big'))

            # Group start block
            self._write_block(f, b'\xc0\x01', self._get_string_bytes("GitHub Languages"))

            for name, col in colors.items():
                # Colour block
                col_bytes = self._get_colour_block_bytes(name, col)
                self._write_block(f, b'\x00\x01', col_bytes)
                
            # Group end block
            self._write_block(f, b'\xc0\x02', b'')
    
    def _write_block(self, file: BinaryIO, block_type_bytes: bytes, block_content_bytes: bytes) -> None:
        file.write(block_type_bytes)
        file.write(len(block_content_bytes).to_bytes(4, byteorder='big'))
        file.write(block_content_bytes)
    
    def _get_string_bytes(self, strval: str) -> bytes:
        b = b''
        b += (len(strval) + 1).to_bytes(2, byteorder='big')
        b += strval.encode('utf-16-be')
        b += b'\x00\x00'
        return b
    
    def _get_colour_block_bytes(self, name: str, color: Color) -> bytes:
        rgb = color.rgb

        b = self._get_string_bytes(name)

        # Colour model - RGB
        b += b'\x52\x47\x42\x20'

        b += struct.pack('>f', rgb[0])
        b += struct.pack('>f', rgb[1])
        b += struct.pack('>f', rgb[2])

        # Colour type: 2 = normal
        b += int(2).to_bytes(2, byteorder='big')

        return b

class AcoGenerator:
    def generate_file(self, colors: dict[str, Color], path: str) -> None:
        with open(path, "wb") as f:
            self._write_v1_section(f, colors)
            self._write_v2_section(f, colors)
    
    def _write_v1_section(self, file: BinaryIO, colors: dict[str, Color]) -> None:
        self._write_header(file, 1, len(colors))
        for col in colors.values():
            self._write_color(file, col)
    
    def _write_v2_section(self, file: BinaryIO, colors: dict[str, Color]) -> None:
        self._write_header(file, 2, len(colors))
        for name, col in colors.items():
            self._write_color(file, col)
            self._write_color_name(file, name)
    
    def _write_header(self, file: BinaryIO, version: int, col_count: int) -> None:
        file.write(struct.pack('>H', version))
        file.write(struct.pack('>H', col_count))
    
    def _write_color(self, file: BinaryIO, color: Color) -> None:
        rgb = tuple(int(c * 65535) for c in  color.rgb)
        file.write(struct.pack('>H', 0))        # Indicates colour is RGB
        file.write(struct.pack('>H', rgb[0]))   # Red component
        file.write(struct.pack('>H', rgb[1]))   # Green component
        file.write(struct.pack('>H', rgb[2]))   # Blue component
        file.write(struct.pack('>H', 0))        # Colours are 4 values long: pad fourth with zero
    
    def _write_color_name(self, file: BinaryIO, name: str) -> None:
        file.write(struct.pack('>I', len(name) + 1))
        file.write(name.encode('utf-16-be'))
        file.write(b'\x00\x00')

class JsonGenerator:
    def generate_file(self, colors: dict[str, Color], path: str) -> None:
        with open(path, "w") as f:
            json.dump({name: col.hex for name, col in colors.items()}, f, indent=4)

class CsvGenerator:
    def generate_file(self, colors: dict[str, Color], path: str) -> None:
        with open(path, "w", newline="\n") as f:
            f.write("Language,R,G,B,Hex\n")
            for name, col in colors.items():
                row = (name, *tuple(str(int(c * 255)) for c in  col.rgb), col.hex)
                f.write(",".join(row) + "\n")


def generator_for_format(format: str) -> PaletteGenerator | None:
    """Return the appropriate generator class for the given format"""
    if format == "ccxml":
        return CcxmlGenerator()
    if format == "gpl":
        return GplGenerator()
    if format == "ase":
        return AseGenerator()
    if format == "aco":
        return AcoGenerator()
    if format == "json":
        return JsonGenerator()
    if format == "csv":
        return CsvGenerator()
    return None


def data_to_color_dict(data) -> dict[str, Color]:
    """Converts the raw deserialised YAML data into a sorted dictionary of colour names and values"""
    return {name: Color(data["color"]) for name, data in sorted(data.items(), key=lambda x: x[0].lower()) if "color" in data}


def get_linguist_language_colours(langs_url: str) -> dict[str, Color]:
    """Fetches the languages YAML from GitHub and returns a dictionary of colour names and values"""
    with urllib.request.urlopen(langs_url) as response:
        raw = response.read()
        data = yaml.safe_load(raw)
        return data_to_color_dict(data)

def load_linguist_language_colours(langs_file: str) -> dict[str, Color]:
    """Loads the languages YAML from a local file and returns a dictionary of colour names and values"""
    with open(langs_file, "r") as f:
        data = yaml.safe_load(f)
        return data_to_color_dict(data)


def get_linguist_popular_languages(popular_url: str) -> list[str]:
    """Fetches the popular languages YAML from GitHub and returns a list of language names"""
    with urllib.request.urlopen(popular_url) as response:
        raw = response.read()
        return yaml.safe_load(raw)

def load_linguist_popular_languages(popular_file: str) -> list[str]:
    """Loads the popular languages YAML from a local file and returns a list of language names"""
    with open(popular_file, "r") as f:
        return yaml.safe_load(f)


def order_language_colours(data: dict[str, Color], popular_langs: list[str]) -> dict[str, Color]:
    """Orders the colours ensuring that the popular languages are at the top of the list"""
    order_set = set(popular_langs)
    ordered_keys = [key for key in popular_langs if key in data]
    remaining_keys = sorted(key for key in data if key not in order_set)
    return {key: data[key] for key in [*ordered_keys, *remaining_keys]}


def run(argv: Sequence[str]) -> int:
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
    
    args = parser.parse_args(argv)

    try:
        # Load the linguist language colours from file or URL
        if args.languages_file is not None:
            linguist_data = load_linguist_language_colours(args.languages_file)
        else:
            linguist_data = get_linguist_language_colours(args.languages_url)

        # Load the popular languages list from file or URL
        if args.popular_file is not None:
            popular_languages = load_linguist_popular_languages(args.popular_file)
        else:
            popular_languages = get_linguist_popular_languages(args.popular_url)

        # Create the final ordered dictionary of colours
        final_data = order_language_colours(linguist_data, popular_languages)

        # Create the appropriate generator and generate the palette file
        generator = generator_for_format(args.format)
        if generator is not None:
            generator.generate_file(final_data, args.output)
            print(f"Created {args.output}")
        else:
            raise ValueError(f"Unknown format '{args.format}'")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0
