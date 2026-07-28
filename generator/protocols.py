from pathlib import Path
from typing import Protocol
from colour import Color


class PaletteGenerator(Protocol):
    def generate_file(self, colors: dict[str, Color], path: Path) -> None: ...
