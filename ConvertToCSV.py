########################################################################################################################
# Copyright (c) Martin Bustos @FronkonGames <fronkongames@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
########################################################################################################################
__author__ = "Martin Bustos <fronkongames@gmail.com>"
__copyright__ = "Copyright 2022, Martin Bustos"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "fronkongames@gmail.com"

import sys
import os
import json
import argparse

def ProgressBar(count, total):
  bar_len = 100
  filled_len = int(round(bar_len * count / float(total)))

  percents = round(100.0 * count / float(total), 1)
  bar = '█' * filled_len + '░' * (bar_len - filled_len)

  sys.stdout.write(f'{bar} {percents}%\r')
  sys.stdout.flush()

def WriteString(app, key):
  value = ''
  if key in app:
    value = str(app[key]).replace('"', '').replace('\n', ' ').replace('\r', ' ').strip()
  return f'"{value}"'

def WriteStringArray(app, key):
  values = []
  for value in app[key]:
    values.append(value.replace('"', '').replace('\n', ' ').replace('\r', ' ').strip())

  text = ','.join(values)
  return f'"{text}"'

def WriteKey(app, key):
  return str(app[key]) if key in app else '0'

print(f'Convert JSON to CSV {__version__} by {__author__}.')
parser = argparse.ArgumentParser(description='Convert JSON to CSV.')
parser.add_argument('-f', '--file', type=str, default='games.json', help='Dataset file name')
args = parser.parse_args()

dataset = {}

filename = args.file
if os.path.exists(filename):
  print(f'Loading dataset.')
  with open(filename, 'r', encoding='utf-8') as fin:
    text = fin.read()
    if len(text) > 0:
      dataset = json.loads(text)

  print(f'Dataset with {len(dataset)} games loaded.')

  with open('games.csv', 'w', encoding="utf-8") as fin:
    header = [
      'AppID',
      'Name',
      'Release date',
      'Required age',
      'Price',
      'DLC count',
      'About the game',
      'Supported languages',
      'Full audio languages',
      'Reviews',
      'Header image',
      'Website',
      'Support url',
      'Support email',
      'Windows',
      'Mac',
      'Linux',
      'Metacritic score',
      'Metacritic url',
      'Achievements',
      'Recommendations',
      'Notes',
      'Developers',
      'Publishers',
      'Categories',
      'Genres',
      'Screenshots',
      'Movies'
    ]

    fin.write(','.join(header) + '\n')

    count = 0
    total = len(dataset)
    for appID in dataset:
      app = dataset[appID]
      fin.write(f"{appID},{WriteString(app, 'name')},{WriteString(app, 'release_date')},{WriteKey(app, 'required_age')}," +
                f"{WriteKey(app, 'price')},{WriteKey(app, 'dlc_count')},{WriteString(app, 'about_the_game')}," +
                f"{WriteString(app, 'supported_languages')},{WriteString(app, 'full_audio_languages')}{WriteString(app, 'reviews')}," +
                f"{WriteString(app, 'header_image')},{WriteString(app, 'website')},{WriteString(app, 'support_url')},"+ 
                f"{WriteString(app, 'support_email')},{WriteKey(app, 'windows')},{WriteKey(app, 'mac')},{WriteKey(app, 'linux')}," + 
                f"{WriteKey(app, 'metacritic_score')},{WriteString(app, 'metacritic_url')},{WriteKey(app, 'achievements')}," +
                f"{WriteKey(app, 'recommendations')},{WriteString(app, 'notes')},{WriteStringArray(app, 'developers')}," +
                f"{WriteStringArray(app, 'publishers')},{WriteStringArray(app, 'categories')},{WriteStringArray(app, 'genres')}," +
                f"{WriteStringArray(app, 'screenshots')},{WriteStringArray(app, 'movies')}\n")
      count += 1
      ProgressBar(count, total)
  
    print('\nDone.')
else:
  print(f'Dataset file \'{args.file}\' not found.')