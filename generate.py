import argparse
import requests
import yaml
from colour import Color
import xml.etree.ElementTree as ET
import json

class CcxmlGenerator:
    PALETTE_XML_NS = "http://markembling.info/xmlschema/colourchooser/palette/1"

    def generate_file(self, colors, path):
        el_palette = ET.Element(self._element_name_namespaced("palette"))

        for lang, col in colors.items():
            el_colour = self._create_colour_element(lang, col)
            el_palette.append(el_colour)

        tree = ET.ElementTree(el_palette)
        tree.write(path, xml_declaration=True,
                         encoding='utf-8',
                         method="xml",
                         default_namespace=self.PALETTE_XML_NS)

    def _element_name_namespaced(self, name):
        return "{{{0}}}{1}".format(self.PALETTE_XML_NS, name)
    
    def _create_colour_element(self, name, color):
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
    def generate_file(self, colors, path):
        with open(path, "w", newline="\n") as f:
            f.write("GIMP Palette\n")
            f.write("# See https://github.com/markembling/github-languages-palette\n")
            for name, col in colors.items():
                rgb = tuple(int(c * 255) for c in  col.rgb)
                f.write(f"{self._pad_number(rgb[0])} {self._pad_number(rgb[1])} {self._pad_number(rgb[2])} {name}\n")

    def _pad_number(self, num):
        return str(num).rjust(3)


class JsonGenerator:
    def generate_file(self, colors, path):
        with open(path, "w") as f:
            json.dump({name: col.hex for name, col in colors.items()}, f, indent=4)


class CsvGenerator:
    def generate_file(self, colors, path):
        with open(path, "w", newline="\n") as f:
            f.write("Language,R,G,B,Hex\n")
            for name, col in colors.items():
                row = (name, *tuple(str(int(c * 255)) for c in  col.rgb), col.hex)
                f.write(",".join(row) + "\n")


def generator_for_format(format):
    """Return the appropriate generator class for the given format"""
    if format == "ccxml":
        return CcxmlGenerator()
    if format == "gpl":
        return GplGenerator()
    if format == "json":
        return JsonGenerator()
    if format == "csv":
        return CsvGenerator()
    return None

def data_to_color_dict(data):
    """Converts the raw deserialised YAML data into a sorted dictionary of colour names and values"""
    return {name: Color(data["color"]) for name, data in sorted(data.items(), key=lambda x: x[0].lower()) if "color" in data}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a palette file for GitHub language colours.",
                                     epilog="Mark Embling (markembling.info)")
    parser.add_argument("output", help="output filename")
    parser.add_argument("--format", help="palette format (default: ccxml)", 
                                    default="ccxml",
                                    choices=["ccxml", "gpl", "json", "csv"])
    parser.add_argument("--url", help="URL for source YAML (default: URL for raw linguist file on GitHub)", 
                                 default="https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml")
    args = parser.parse_args()

    response = requests.get(args.url)
    data = yaml.safe_load(response.text)
    color_dict = data_to_color_dict(data)

    generator = generator_for_format(args.format)
    generator.generate_file(color_dict, args.output)
    print(f"Created {args.output}")
