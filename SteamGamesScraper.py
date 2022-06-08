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
import re
from ssl import SSLError
import requests
import json
import time
import traceback
import argparse
import random
import datetime as dt

DEFAULT_OUTFILE  = 'games.json'
APPLIST_FILE     = 'applist.json'
DISCARTED_FILE   = 'discarted.json'
NOTRELEASED_FILE = 'notreleased.json'
DEFAULT_SLEEP    = 5.0
DEFAULT_RETRIES  = 4
DEFAULT_AUTOSAVE = 100
DEFAULT_TIMEOUT  = 10
DEFAULT_CURRENCY = 'us'
LOG_ICON         = ['i', 'W', '!', '!!']
INFO             = 0
WARNING          = 1
ERROR            = 2
EXCEPTION        = 3

def Log(level, message):
  print(f"[{LOG_ICON[level]} {dt.datetime.now().strftime('%H:%M:%S')}] {message}.")

def ProgressBar(title, count, total):
  bar_len = 100
  filled_len = int(round(bar_len * count / float(total)))

  percents = round(100.0 * count / float(total), 2)
  bar = '█' * filled_len + '░' * (bar_len - filled_len)

  sys.stdout.write(f"[i {dt.datetime.now().strftime('%H:%M:%S')}] {title} {bar} {percents}% (CTRL+C to exit). \r")
  sys.stdout.flush()

def SanitizeText(text):
  '''
  Eliminates HTML codes, escape codes and URLs.
  '''
  text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', text, flags=re.MULTILINE)
  text = re.sub('<[^<]+?>', '', text)
  text = text.replace('\n\r', ' ')
  text = text.replace('\r\n', ' ')
  text = text.replace('\r \n', ' ')
  text = text.replace('\t', ' ')
  text = text.replace('&quot;', "'")
  text = re.sub(' +', ' ', text)
  text = text.lstrip(' ')

  return text

def DoRequest(url, parameters=None, retryTime=5, successCount=0, errorCount=0, retries=0):
  '''
  Makes a Web request. If an error occurs, retry.
  '''
  response = None
  try:
    response = requests.get(url=url, params=parameters, timeout=DEFAULT_TIMEOUT)
  except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
          requests.exceptions.Timeout, requests.exceptions.RequestException,
          SSLError) as ex:
    Log(EXCEPTION, f'An exception of type {type(ex).__name__} ocurred.')
    response = None

  if response and response.status_code == 200:
    errorCount = 0
    successCount += 1
    if successCount > retryTime:
      retryTime = min(5, retryTime / 2)
      successCount = 0
  else:
    if retries == 0 or errorCount < retries:
      errorCount += 1
      successCount = 0
      retryTime = min(retryTime * 2, 500)
      if response is not None:
        Log(WARNING, f'{response.reason}, retrying in {retryTime} seconds')
      else:
        Log(WARNING, f'Request failed, retrying in {retryTime} seconds.')

      time.sleep(retryTime)

      return DoRequest(url, parameters, retryTime, successCount, errorCount, retries)
    else:
      print('[!] No more retries.')
      sys.exit()

  return response

def SteamRequest(appID, retryTime, successRequestCount, errorRequestCount, retries, currency='us', language='en'):
  '''
  Request and parse information about a Steam app.
  '''
  url = "http://store.steampowered.com/api/appdetails/"
  response = DoRequest(url, {"appids": appID, "cc": currency, "l": language}, retryTime, successRequestCount, errorRequestCount, retries)
  if response:
    try:
      data = response.json()
      app = data[appID]
      if app['success'] == False:
        return None
      elif app['data']['type'] != 'game':
        return None
      elif app['data']['is_free'] == False and 'price_overview' in app['data'] and app['data']['price_overview']['final_formatted'] == '':
        return None
      elif 'developers' in app['data'] and len(app['data']['developers']) == 0:
        return None
      else:
        return app['data']
    except Exception as ex:
      Log(EXCEPTION, f'An exception of type {ex} ocurred. Traceback: {traceback.format_exc()}')
      return None
  else:
    Log(ERROR, 'Bad response')
    return None

def ParseGame(app):
  '''
  Parse game info.
  '''
  game = {}
  game['name'] = app['name'].strip()
  game['release_date'] = app['release_date']['date'] if 'release_date' in app and not app['release_date']['coming_soon'] else ''
  game['required_age'] = int(str(app['required_age']).replace('+', '')) if 'required_age' in app else 0

  if app['is_free'] or 'price_overview' not in app:
    game['price'] = 0.0
  else:
    game['price'] = round(float(re.findall('([0-9]+[,.]+[0-9]+)', app['price_overview']['final_formatted'])[0]), 2)

  game['dlc_count'] = len(app['dlc']) if 'dlc' in app else 0
  game['detailed_description'] = app['detailed_description'].strip() if 'detailed_description' in app else ''
  game['about_the_game'] = app['about_the_game'].strip() if 'about_the_game' in app else ''
  game['short_description'] = app['short_description'].strip() if 'short_description' in app else ''
  game['reviews'] = app['reviews'].strip() if 'reviews' in app else ''
  game['header_image'] = app['header_image'].strip() if 'header_image' in app else ''
  game['website'] = app['website'].strip() if 'website' in app and app['website'] is not None else ''
  game['support_url'] = app['support_info']['url'].strip() if 'support_info' in app else ''
  game['support_email'] = app['support_info']['email'].strip() if 'support_info' in app else ''
  game['windows'] = True if app['platforms']['windows'] else False
  game['mac'] = True if app['platforms']['mac'] else False
  game['linux'] = True if app['platforms']['linux'] else False
  game['metacritic_score'] = int(app['metacritic']['score']) if 'metacritic' in app else 0
  game['metacritic_url'] = app['metacritic']['url'] if 'metacritic' in app else ''
  game['achievements'] = int(app['achievements']['total']) if 'achievements' in app else 0
  game['recommendations'] = app['recommendations']['total'] if 'recommendations' in app else 0
  game['notes'] = app['content_descriptors']['notes'] if 'content_descriptors' in app and app['content_descriptors']['notes'] is not None else ''

  game['detailed_description'] = SanitizeText(game['detailed_description'])
  game['about_the_game'] = SanitizeText(game['about_the_game'])
  game['reviews'] = SanitizeText(game['reviews'])
  game['notes'] = SanitizeText(game['notes'])

  game['supported_languages'] = []
  game['full_audio_languages'] = []

  if 'supported_languages' in app:
    languagesApp = app['supported_languages']
    languagesApp = re.sub('<[^<]+?>', '', languagesApp)
    languagesApp = languagesApp.replace('languages with full audio support', '')

    languages = languagesApp.split(', ')
    for lang in languages:
      if '*' in lang:
        game['full_audio_languages'].append(lang.replace('*', ''))
      game['supported_languages'].append(lang.replace('*', ''))

  game['packages'] = []
  if 'package_groups' in app:
    for package in app['package_groups']:
      subs = []
      if 'subs' in package:
        for sub in package['subs']:
          subs.append({'text': sub['option_text'],
                       'description': sub['option_description'],
                       'price': round(float(sub['price_in_cents_with_discount']) * 0.01, 2) })

      game['packages'].append({'title': SanitizeText(package['title']), 'description': SanitizeText(package['description']), 'subs': subs})

  game['developers'] = []
  if 'developers' in app:
    for developer in app['developers']:
      game['developers'].append(developer.strip())

  game['publishers'] = []
  if 'publishers' in app:
    for publisher in app['publishers']:
      game['publishers'].append(publisher.strip())

  game['categories'] = []
  if 'categories' in app:
    for category in app['categories']:
      game['categories'].append(category['description'])

  game['genres'] = []
  if 'genres' in app:
    for genre in app['genres']:
      game['genres'].append(genre['description'])

  game['screenshots'] = []
  if 'screenshots' in app:
    for screenshot in app['screenshots']:
      game['screenshots'].append(screenshot['path_full'])

  game['movies'] = []
  if 'movies' in app:
    for movie in app['movies']:
      game['movies'].append(movie['mp4']['max'])

  return game

def SaveJSON(data, filename, backup = False):
  try:
    if backup == True and os.path.exists(filename):
      name, ext = os.path.splitext(filename)
      os.replace(filename, name + '.bak')

    with open(filename, 'w', encoding='utf-8') as fout:
      fout.seek(0)
      fout.write(json.dumps(data, indent=4, ensure_ascii=False))
      fout.truncate()
  except Exception as ex:
    Log(EXCEPTION, f'An exception of type {ex} ocurred. Traceback: {traceback.format_exc()}')
    sys.exit()

def LoadJSON(filename):
  '''
  Load a file with discarded apps.
  '''
  data = None
  try:
    if os.path.exists(filename):
      Log(INFO, f"Loading '{filename}'")
      with open(filename, 'r', encoding='utf-8') as fin:
        text = fin.read()
        if len(text) > 0:
          data = json.loads(text)
  except Exception as ex:
    Log(EXCEPTION, f'An exception of type {ex} ocurred. Traceback: {traceback.format_exc()}')
    sys.exit()

  return data

def Scraper(dataset, notreleased, discarted, args):
  '''
  Search games in Steam.
  '''
  apps = []
  if os.path.exists(APPLIST_FILE):
    with open(APPLIST_FILE, 'r', encoding='utf-8') as fin:
      text = fin.read()
      if len(text) > 0:
        apps = json.loads(text)
        Log(INFO, f'List with {len(apps)} games loaded')
  else:
    Log(INFO, 'Requesting list of games from Steam')
    response = DoRequest('http://api.steampowered.com/ISteamApps/GetAppList/v2/')
    if response:
      time.sleep(args.sleep)
      data = response.json()
      apps = data['applist']['apps']
      apps = [str(x["appid"]) for x in apps]
      with open(APPLIST_FILE, 'w', encoding='utf-8') as fout:
        fout.seek(0)
        fout.write(json.dumps(apps, indent=4, ensure_ascii=False))
        fout.truncate()

  if apps:
    gamesAdded = 0
    gamesNotReleased = 0
    gamesDiscarted = 0
    successRequestCount = 0
    errorRequestCount = 0

    random.shuffle(apps)
    total = len(apps)
    count = 0

    for appID in apps:
      if appID not in dataset and appID not in discarted:
        if args.released and appID in notreleased:
          continue

        app = SteamRequest(appID, min(4, args.sleep), successRequestCount, errorRequestCount, args.retries)
        if app:
          game = ParseGame(app)
          if game['release_date'] != '':
            dataset[appID] = game
            gamesAdded += 1

            if appID in notreleased:
              notreleased.remove(appID)

            if args.autosave > 0 and gamesAdded > 0 and gamesAdded % args.autosave == 0:
              SaveJSON(dataset, args.outfile, True)
          else:
            if appID not in notreleased:
              notreleased.append(appID)
              gamesNotReleased += 1

              if args.autosave > 0 and gamesNotReleased > 0 and gamesNotReleased % args.autosave == 0:
                SaveJSON(notreleased, NOTRELEASED_FILE, True)

            text = f"'{game['name']}' is not released yet"
        else:
          discarted.append(appID)
          gamesDiscarted += 1

        if args.autosave > 0 and gamesDiscarted > 0 and gamesDiscarted % args.autosave == 0:
          SaveJSON(discarted, DISCARTED_FILE, True)

        time.sleep(args.sleep if random.random() > 0.1 else args.sleep * 2.0)
      count += 1
      ProgressBar('Scanning', count, total)

    ProgressBar('Scanning', total, total)
    print('\r')
    Log(INFO, f'Scanning completed: {gamesAdded} new games added, {gamesNotReleased} not released, {gamesDiscarted} discarted')
    SaveJSON(dataset, args.outfile)
    SaveJSON(discarted, DISCARTED_FILE)
    SaveJSON(notreleased, NOTRELEASED_FILE)
  else:
    Log(ERROR, 'Error requesting list of games')
    sys.exit()

if __name__ == "__main__":
  print(f'Steam Games Scraper {__version__} by {__author__}.')
  parser = argparse.ArgumentParser(description='Steam games scraper.')
  parser.add_argument('-o', '--outfile',     type=str,   default=DEFAULT_OUTFILE,  help='Output file name')
  parser.add_argument('-s', '--sleep',       type=float, default=DEFAULT_SLEEP,    help='Waiting time between requests')
  parser.add_argument('-r', '--retries',     type=int,   default=DEFAULT_RETRIES,  help='Number of retries (0 to always retry)')
  parser.add_argument('-a', '--autosave',    type=int,   default=DEFAULT_AUTOSAVE, help='Record the data every number of new entries (0 to deactivate)')
  parser.add_argument('-d', '--released',    type=bool,  default=True,             help='If it is on the list of not yet released, no information is requested')
  parser.add_argument('-c', '--currency',    type=str,   default=DEFAULT_CURRENCY, help='Currency code')
  args = parser.parse_args()
  random.seed(time.time())

  if 'h' in args or 'help' in args:
    parser.print_help()
    sys.exit()

  dataset = LoadJSON(args.outfile)
  discarted = LoadJSON(DISCARTED_FILE)
  notreleased = LoadJSON(NOTRELEASED_FILE)

  if dataset is None:
    dataset = {}

  if discarted is None:
    discarted = []

  if notreleased is None:
    notreleased = []

  Log(INFO, f'Dataset loaded with {len(dataset)} games' if len(dataset) > 0 else 'New dataset created')

  if len(notreleased) > 0:
    Log(INFO, f'{len(notreleased)} games not released yet')

  if len(discarted) > 0:
    Log(INFO, f'{len(discarted)} apps discarted')

  try:
    Scraper(dataset, notreleased, discarted, args)
  except (KeyboardInterrupt, SystemExit):
    SaveJSON(dataset, args.outfile, args.autosave > 0)
    SaveJSON(discarted, DISCARTED_FILE, args.autosave > 0)
    SaveJSON(notreleased, NOTRELEASED_FILE, args.autosave > 0)

  Log(INFO, 'Done\r')
