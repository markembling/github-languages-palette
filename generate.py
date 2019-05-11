import struct
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


class AseGenerator:
    def generate_file(self, colors, path):
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
    
    def _write_block(self, file, block_type_bytes, block_content_bytes):
        file.write(block_type_bytes)
        file.write(len(block_content_bytes).to_bytes(4, byteorder='big'))
        file.write(block_content_bytes)
    
    def _get_string_bytes(self, strval):
        b = b''
        b += (len(strval) + 1).to_bytes(2, byteorder='big')
        b += strval.encode('utf-16-be')
        b += b'\x00\x00'
        return b
    
    def _get_colour_block_bytes(self, name, color):
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
    def generate_file(self, colors, path):
        with open(path, "wb") as f:
            self._write_v1_section(f, colors)
            self._write_v2_section(f, colors)
    
    def _write_v1_section(self, file, colors):
        self._write_header(file, 1, len(colors))
        for col in colors.values():
            self._write_color(file, col)
    
    def _write_v2_section(self, file, colors):
        self._write_header(file, 2, len(colors))
        for name, col in colors.items():
            self._write_color(file, col)
            self._write_color_name(file, name)
    
    def _write_header(self, file, version, col_count):
        file.write(struct.pack('>H', version))
        file.write(struct.pack('>H', col_count))
    
    def _write_color(self, file, color):
        rgb = tuple(int(c * 65535) for c in  color.rgb)
        file.write(struct.pack('>H', 0))        # Indcates colour is RGB
        file.write(struct.pack('>H', rgb[0]))   # Red component
        file.write(struct.pack('>H', rgb[1]))   # Green component
        file.write(struct.pack('>H', rgb[2]))   # Blue component
        file.write(struct.pack('>H', 0))        # Colours are 4 values long: pad fourth with zero
    
    def _write_color_name(self, file, name):
        file.write(struct.pack('>I', len(name) + 1))
        file.write(name.encode('utf-16-be'))
        file.write(b'\x00\x00')


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
    if format == "ase":
        return AseGenerator()
    if format == "aco":
        return AcoGenerator()
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
                                    choices=["ccxml", "gpl", "ase", "aco", "json", "csv"])
    parser.add_argument("--url", help="URL for source YAML (default: URL for raw linguist file on GitHub)", 
                                 default="https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml")
    args = parser.parse_args()

    response = requests.get(args.url)
    data = yaml.safe_load(response.text)
    color_dict = data_to_color_dict(data)

    generator = generator_for_format(args.format)
    generator.generate_file(color_dict, args.output)
    print(f"Created {args.output}")
