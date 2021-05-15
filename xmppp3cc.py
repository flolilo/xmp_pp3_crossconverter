#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
from pathlib import Path
from argparse import ArgumentParser

# DK to RT or RT to DK? Make it a choice via argument!
parser = ArgumentParser()
parser.add_argument("--metadata_source",
                    dest="metadata_source",
                    default="XMP",
                    help="Source. Use 'XMP' for DigiKam, or 'PP3' for RawTherapee.")
parser.add_argument("--main_path",
                    dest="main_path",
                    default="./",
                    help="Path that the script handles.")
parser.add_argument("--verbose",
                    dest="verbose",
                    type=int,
                    default=0,
                    help="A bit of verbose.")
metadata_source = parser.parse_args().metadata_source
if(parser.parse_args().verbose > 0):
    f = sys.stdout
else:
    f = open(os.devnull, 'w')

if(metadata_source not in ["XMP", "PP3"]):
    input("Incorrect choice of --metadata_source!")
    sys.exit(1)

main_path = parser.parse_args().main_path
if(not Path(main_path).is_dir):
    input("Incorrect choice of --main_path!")
    sys.exit(1)

# Find only *.pp3 and *.xmp in this folder, keep only those that have a twin with the other extension:
try:
    found_pp3 = [str(x.resolve()) for x in Path(main_path).glob('*.pp3') if
                 Path(re.sub('\.pp3$', '.xmp', str(x.resolve()), flags=re.MULTILINE)).is_file()]
    found_xmp = [str(x.resolve()) for x in Path(main_path).glob('*.xmp') if
                 Path(re.sub('\.xmp$', '.pp3', str(x.resolve()), flags=re.MULTILINE)).is_file()]
    # Making sure that A.pp3 is used as the same time as A.xmp:
    found_pp3 = sorted(found_pp3, key=str.lower)
    found_xmp = sorted(found_xmp, key=str.lower)
except Exception:
    print("Something already went wrong...")
    sys.exit(1)

print(str(len(found_pp3)) + " | " + str(len(found_xmp)) + " files found.")
input("If that sounds about right, press enter to continue.")


# Make functions for both directions to reduce load on while-loop:
def XMP_PP3_crossconversion(source_file, target_file,
                            source_regex_stars, source_regex_color,
                            target_regex_stars, target_regex_color):
    global metadata_source
    global f
    # Substituting Stars (aka rank/rating):
    try:
        source_temp = re.search(source_regex_stars, source_file).group(1)
    except Exception:
        source_temp = "0"
        pass
    print("Stars: " + source_temp, file=f)
    target_temp = re.sub(target_regex_stars[0], target_regex_stars[1] + source_temp, target_file)
    # Substituting color-tags:
    try:
        source_temp = re.search(source_regex_color, source_file).group(1)
    except Exception:
        source_temp = "0"
        pass
    # DigiKam has 0-9 tags, RawTherapee 0-5.
    # Translate orange to yellow and grey/white/black to none:
    if(metadata_source == "XMP"):
        if(int(source_temp) == 3):
            source_temp = "4"
        elif(3 < int(source_temp) <= 6):
            source_temp = str(int(source_temp) - 1)
        elif(int(source_temp) > 6):
            source_temp = "0"
    else:
        if(int(source_temp) > 3):
            source_temp = str(int(source_temp) + 1)
    print("Color: " + source_temp, file=f)
    target_temp = re.sub(target_regex_color[0], target_regex_color[1] + source_temp, target_temp)

    return target_temp


# Fun with regex. This will be the most important part if pp3 or (DigiKam-flavoured) XMP ever change.
xmp_rating_source = 'xmp:Rating=\"(.+?)\"'
pp3_rating_source = 'Rank=(.+?)'
xmp_color_source = 'digiKam:ColorLabel=\"(.+?)\"'
pp3_color_source = 'ColorLabel=(.+?)'
xmp_rating_target = ['xmp:Rating=\"\d', 'xmp:Rating=\"']
pp3_rating_target = ['Rank=\d', 'Rank=']
xmp_color_target = ['digiKam:ColorLabel=\"\d', 'digiKam:ColorLabel=\"']
pp3_color_target = ['ColorLabel=\d', 'ColorLabel=']

if(metadata_source == "XMP"):
    source_rating = xmp_rating_source
    target_rating = pp3_rating_target
    source_color = xmp_color_source
    target_color = pp3_color_target
    source_paths = found_xmp
    target_paths = found_pp3
else:
    source_rating = pp3_rating_source
    target_rating = xmp_rating_target
    source_color = pp3_color_source
    target_color = xmp_color_target
    source_paths = found_pp3
    target_paths = found_xmp

# This is where the fun begins:
i = 0
while i < len(found_pp3):
    print(source_paths[i] + " to " + target_paths[i], file=f)  # Verbose
    # Copying content of 1st/2nd/... file into variable:
    source_strings = Path(source_paths[i]).read_text(encoding='utf-8')
    target_strings = Path(target_paths[i]).read_text(encoding='utf-8')

    target_temp = XMP_PP3_crossconversion(source_strings, target_strings, source_rating,
                                          source_color, target_rating, target_color)
    # Overwriting the target:
    Path(target_paths[i]).write_text(target_temp, encoding='utf-8')

    i += 1

print("Done!")
