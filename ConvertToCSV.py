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
__version__ = "1.1.0"
__email__ = "fronkongames@gmail.com"

import sys
import os
import json
import argparse

def ProgressBar(count, total):
  bar_len = 50
  filled_len = int(round(bar_len * count / float(total)))

  percents = round(100.0 * count / float(total), 1)
  bar = '█' * filled_len + '░' * (bar_len - filled_len)

  sys.stdout.write(f'{bar} {percents}%\r')
  sys.stdout.flush()

def WriteString(app, key, default = ''):
  value = default
  if key in app and app[key] != None and app[key] != '':
    value = str(app[key]).replace('"', '').replace('\n', ' ').replace('\r', ' ').strip()
  return f'"{value}"'

def WriteStringArray(app, key):
  values = []
  for value in app[key]:
    if value != None:
      values.append(value.replace('"', '').replace('\n', ' ').replace('\r', ' ').strip())

  text = ','.join(values)
  return f'"{text}"'

def WriteKey(app, key, default = '0'):
  return str(app[key]) if key in app else default

print(f'Convert JSON to CSV {__version__} by {__author__}.')
parser = argparse.ArgumentParser(description='Convert JSON to CSV.')
parser.add_argument('-f', '--file', type=str, default='games.json', help='Dataset file name')
args = parser.parse_args()

dataset = {}

filename = args.file
if os.path.exists(filename):
  print('Loading dataset.')
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
      'Estimated owners',
      'Peak CCU',
      'Required age',
      'Price',
      'Discount'
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
      'User score',
      'Positive',
      'Negative',
      'Score rank',
      'Achievements',
      'Recommendations',
      'Notes',
      'Average playtime forever',
      'Average playtime two weeks',
      'Median playtime forever',
      'Median playtime two weeks',
      'Developers',
      'Publishers',
      'Categories',
      'Genres',
      'Tags',
      'Screenshots',
      'Movies'
    ]

    fin.write(','.join(header) + '\n')

    count = 0
    total = len(dataset)
    for appID in dataset:
      app = dataset[appID]

      data = f"{appID},"
      data += f"{WriteString(app, 'name')},"
      data += f"{WriteString(app, 'release_date')},"
      data += f"{WriteString(app, 'estimated_owners')},"
      data += f"{WriteKey(app, 'peak_ccu')},"
      data += f"{WriteKey(app, 'required_age')},"
      data += f"{WriteKey(app, 'price', '0.0')},"
      data += f"{WriteKey(app, 'discount')},"
      data += f"{WriteKey(app, 'dlc_count')},"
      data += f"{WriteString(app, 'about_the_game')},"
      data += f"{WriteString(app, 'supported_languages')},"
      data += f"{WriteString(app, 'full_audio_languages')},"
      data += f"{WriteString(app, 'reviews')},"
      data += f"{WriteString(app, 'header_image')},"
      data += f"{WriteString(app, 'website')},"
      data += f"{WriteString(app, 'support_url')},"
      data += f"{WriteString(app, 'support_email')},"
      data += f"{WriteKey(app, 'windows', 'False')},"
      data += f"{WriteKey(app, 'mac', 'False')},"
      data += f"{WriteKey(app, 'linux', 'False')},"
      data += f"{WriteKey(app, 'metacritic_score')},"
      data += f"{WriteString(app, 'metacritic_url')},"
      data += f"{WriteKey(app, 'user_score')},"
      data += f"{WriteKey(app, 'positive')},"
      data += f"{WriteKey(app, 'negative')},"
      data += f"{WriteString(app, 'score_rank')},"
      data += f"{WriteKey(app, 'achievements')},"
      data += f"{WriteKey(app, 'recommendations')},"
      data += f"{WriteString(app, 'notes')},"
      data += f"{WriteKey(app, 'average_playtime_forever')},"
      data += f"{WriteKey(app, 'average_playtime_2weeks')},"
      data += f"{WriteKey(app, 'median_playtime_forever')},"
      data += f"{WriteKey(app, 'median_playtime_2weeks')},"
      data += f"{WriteStringArray(app, 'developers')},"
      data += f"{WriteStringArray(app, 'publishers')},"
      data += f"{WriteStringArray(app, 'categories')},"
      data += f"{WriteStringArray(app, 'genres')},"
      data += f"{WriteStringArray(app, 'tags')},"
      data += f"{WriteStringArray(app, 'screenshots')},"
      data += f"{WriteStringArray(app, 'movies')}"
      data += "\n"

      fin.write(data)
      count += 1
      ProgressBar(count, total)
  
    print('\nDone.')
else:
  print(f'Dataset file \'{args.file}\' not found.')