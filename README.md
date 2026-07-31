# GitHub Programming Language Colour Palettes

This repository contains palette files in various formats containing the colours
used for all the programming languages on GitHub, extracted directly from
[Linguist](ghl).

It also contains a Python module which generates the palette files from the
original Linguist source YAML.

This was inspired by [doda/github-language-colors](https://github.com/doda/github-language-colors)
but I wanted the output to be something which I could feed straight into various
other apps (primarily my own [Colour Chooser][cc]).

## Palettes

The palette files can be found in the [`palettes`](palettes/) directory in the
following formats. If you're after the colours, this is what you want - just
grab the format(s) you need and use. No need to worry about any of the rest.

 - [Colour Chooser][cc] palette file (`.ccxml`)
 - [GIMP](https://www.gimp.org/) palette (`.gpl`)
 - Adobe Swatch Exchange file (`.ase`)
 - Adobe Photoshop Color Swatch file (`.aco`)
 - JSON file (`.json`)
 - CSV file (`.csv`)

The specific release version of Linguist from which these palettes were
generated is also given in the `UPSTREAM_VERSION` file. This will generally be
the latest release, meaning the colours in the palettes should match what can be
currently seen on GitHub.

If there's a palette format missing that you'd find useful, submit an issue and
I'll see what I can do. Alternatively, feel free to contribute a pull request
adding it.

I've intentionally not included palette formats which do not allow for naming
each colour - it'd miss the point somewhat.

## Palette Generation

The Python module contains the logic for grabbing the languages data from GitHub
and generating the palette files. A single invocation generates one palette file
in a given supported format.

The most convenient way to invoke the generator is via the just recipes:

```sh
# Bootstrap a Python virtualenv in .venv and install dependencies via pip.
# Needed before any subsequent commands.
just bootstrap

# Generate all palette files freshly from the latest Linguist release.
just all-release

# Generate all palette files freshly from the latest on main.
just all

# Invoke the generator with no predefined args (you'll have to provide them -
# these will get you started).
just run --help
just run --format ccxml path/to/output.ccxml
```

By default, the generator will use the latest version of the Linguist data
directly from the main branch on GitHub, however alternative URLs can be
provided. It also supports using local files instead, which take precedence over
the default URLs. In either case, the data must match the format set out by
Linguist.

Palettes will be ordered with the popular languages first, followed by the
others. However if you don't want this, use `--no-popular-first`.

## License

The script for generating the palettes is licensed under the [MIT license](LICENSE).

The actual palette of colours is part of GitHub's [Linguist](ghl) and therefore
usage is dictated by the [license for Linguist](ghllic). To date this has also
been the MIT license.


[ghl]: https://github.com/github-linguist/linguist
[ghllic]: https://github.com/github/linguist/blob/master/LICENSE
[cc]: https://markembling.info/2010/12/colour-chooser
