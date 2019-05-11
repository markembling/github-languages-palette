# GitHub Programming Language Colour Palettes

This repository contains palette files in various formats containing the colours used for all the programming languages on GitHub, along with a Python script which constructs the palette files. Not all languages on GitHub actually have an assigned colour, so only those which do are included.

This was inspired by [doda/github-language-colors](https://github.com/doda/github-language-colors) but I wanted the output to be something which I could feed straight into various other apps (primarily my own [Colour Chooser][cc]). I originally considered putting together just a small script which would download that JSON file and convert it to other formats, but figured I may as well take the colours straight from [the source](https://github.com/github/linguist/blob/master/lib/linguist/languages.yml) and output in a number of formats. The number of formats is likely to grow over time.

## Palettes

The palette files can be found in the [`palettes`](palettes/) directory in the following formats. If you're after the colours, this is where you want to go - just grab the file format which you need and use it and you don't need to worry about the Python script.

 - [Colour Chooser][cc] palette file (`.ccxml`)
 - [GIMP](https://www.gimp.org/) palette (`.gpl`)
 - Adobe Swatch Exchange file (`.ase`)
 - Adobe Photoshop Color Swatch file (`.aco`)
 - JSON file (`.json`)
 - CSV file (`.csv`)

 This should cover most cases but if there's a palette format missing that you'd find useful, add an issue and I'll see what I can do when I have time. Alternatively if you'd like to, feel free to contribute a pull request adding the functionality.

 **Note:** I've purposefully not included palette formats which do not include names for each colour - I thought that missed the point somewhat.

## Python Script

The Python script is what grabs the list from GitHub and generates the palette files. The script generates a single palette file in one of the supported formats or I have also included scripts which will generate all the files.

If you want to run the script, you will first need to:

 1. Have a recent version of Python 3 installed (>= 3.6).
 2. (Optional) Create a [virtual environment](https://docs.python.org/3.7/tutorial/venv.html) and activate it. I'd recommend this so the required packages are not installed system-wide.  
    
        python3 -m venv venv
        . venv/bin/activate

 3. Install the required packages using `pip`.  
    
        pip install -r requirements.txt

Once that's done, you're ready to generate a palette. You can generate either a single palette file or all of them.

### Generating a single palette

Generate a single palette by running the script, telling it which format you want and what output file you want.

    python generate.py --format ccxml path/to/output/file.ccxml

The format is the file extension corresponding to the format you would like. See the 'Palettes' section above for a list of the supported file formats. In the above example, a Colour Chooser palette will be generated.

If you want to use an alternative source URL for the linguist YAML file, you can specify this using the `--url` option. It will however expect the same format so if you feed it something else, it'll probably just complain.

The script can also provide a help message:

    python generate.py --help

### Generating all palette files

I've included some shell scripts which will generate all supported palette files. These are what I use to regenerate the files if GitHub update their colours.

These scripts will create a `palettes` directory if it does not already exist, and then generate the palette files in each format inside with the filename `githublangs.xxx`. If files do exist, they will be overwritten. You can't pass any options to these scripts so if you need to, you'll need to run it as above yourself.

#### Bash

    ./generate-all.sh

#### PowerShell

    ./generate-all.ps1


[cc]: https://markembling.info/2010/12/colour-chooser