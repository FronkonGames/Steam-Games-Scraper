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
__author__    = "Martin Bustos <fronkongames@gmail.com>"
__copyright__ = "Copyright 2022, Martin Bustos"
__license__   = "MIT"
__version__   = "1.3.0"
__email__     = "fronkongames@gmail.com"

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
import csv

# Initialize a global session for connection pooling
session = requests.Session()

DEFAULT_INFILE   = 'games.json'
DEFAULT_OUTFILE  = 'games.json'
APPLIST_FILE     = 'applist.json'
DISCARDED_FILE   = 'discarded.json'
NOTRELEASED_FILE = 'notreleased.json'
DEFAULT_SLEEP    = 1.5
DEFAULT_RETRIES  = 4
DEFAULT_AUTOSAVE = 100
DEFAULT_TIMEOUT  = 10
DEFAULT_CURRENCY = 'us'
DEFAULT_LANGUAGE = 'en'
LOG_ICON         = ['i', 'W', 'E', '!']
INFO             = 0
WARNING          = 1
ERROR            = 2
EXCEPTION        = 3

def Log(level, message):
  '''
  Format and print a log message.
  '''
  print(f"[{LOG_ICON[level]} {dt.datetime.now().strftime('%H:%M:%S')}] {message}")

def ProgressBar(title, count, total):
  '''
  Displays and updates a progress bar.
  '''
  bar_len = 75
  filled_len = int(round(bar_len * count / float(total)))

  percents = round(100.0 * count / float(total), 2)
  bar = '█' * filled_len + '░' * (bar_len - filled_len)

  sys.stdout.write(f"[i {dt.datetime.now().strftime('%H:%M:%S')}] {title} {bar} {percents}% (CTRL+C to exit). \r")
  sys.stdout.flush()

def SanitizeText(text):
  '''
  Removes HTML codes, escape codes and URLs.
  '''
  text = text.replace('\n\r', ' ')
  text = text.replace('\r\n', ' ')
  text = text.replace('\r \n', ' ')
  text = text.replace('\r', ' ')
  text = text.replace('\n', ' ')
  text = text.replace('\t', ' ')
  text = text.replace('&quot;', "'")
  text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', text, flags=re.MULTILINE)
  text = re.sub('<[^<]+?>', ' ', text)
  text = re.sub(' +', ' ', text)
  text = text.lstrip(' ')

  return text

def PriceToFloat(price, decimals=2):
  '''
  Price in text to float. Use locate?
  '''
  price = price.replace(',', '.')

  return round(float(re.findall('([0-9]+[,.]+[0-9]+)', price)[0]), decimals)

def DoRequest(url, parameters=None, retryTime=5, successCount=0, errorCount=0, retries=0):
  '''
  Makes a Web request. If an error occurs, retry.
  '''
  response = None
  try:
    response = session.get(url=url, params=parameters, timeout=DEFAULT_TIMEOUT)
  except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
          requests.exceptions.Timeout, requests.exceptions.RequestException,
          SSLError) as ex:
    Log(EXCEPTION, f'An exception of type {type(ex).__name__} ocurred.')
    response = None

  if response and response.status_code == 200:
    errorCount = 0
    successCount += 1
    if successCount > retryTime:
      retryTime = max(1.5, retryTime / 2)
      successCount = 0
  elif response and response.status_code == 429:
    # Too Many Requests - back off significantly
    retryTime = 60 
    Log(WARNING, f'Rate limit exceeded (429). Waiting {retryTime} seconds...')
    time.sleep(retryTime)
    return DoRequest(url, parameters, retryTime, successCount, errorCount, retries)
  else:
    if retries == 0 or errorCount < retries:
      errorCount += 1
      successCount = 0
      retryTime = min(retryTime * 2, 500)
      if response is not None:
        Log(WARNING, f'HTTP {response.status_code} {response.reason}, retrying in {retryTime} seconds')
      else:
        Log(WARNING, f'Request failed, retrying in {retryTime} seconds.')

      time.sleep(retryTime)

      return DoRequest(url, parameters, retryTime, successCount, errorCount, retries)
    else:
      Log(ERROR, 'No more retries available. Saving and exiting.')
      sys.exit()

  return response

def SteamRequest(appID, retryTime, successRequestCount, errorRequestCount, retries, currency=DEFAULT_CURRENCY, language=DEFAULT_LANGUAGE):
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
        return None, 'no_success', 'Unknown'
      
      app_data = app['data']
      name = app_data.get('name', 'Unknown')
      
      if app_data.get('type') != 'game':
        return None, app_data.get('type', 'not_game'), name
      elif app_data.get('is_free') == False and 'price_overview' in app_data and app_data['price_overview'].get('final_formatted') == '':
        return None, 'no_price', name
      elif 'developers' in app_data and len(app_data['developers']) == 0:
        return None, 'no_developer', name
      else:
        return app_data, 'ok', name
    except Exception as ex:
      Log(EXCEPTION, f'An exception of type {ex} ocurred. Traceback: {traceback.format_exc()}')
      return None, 'exception', 'Unknown'
  else:
    Log(ERROR, 'Bad response')
    return None, 'bad_response', 'Unknown'

def SteamSpyRequest(appID, retryTime, successRequestCount, errorRequestCount, retries):
  '''
  Request and parse information about a Steam app using SteamSpy.
  '''
  url = f"https://steamspy.com/api.php?request=appdetails&appid={appID}"
  response = DoRequest(url, None, retryTime, successRequestCount, errorRequestCount, retries)
  if response:
    try:
      data = response.json()
      if data['developer'] != "":
        return data
      else:
        return None
    except Exception as ex:
      Log(EXCEPTION, f'An exception of type {ex} ocurred. Traceback: {traceback.format_exc()}')
      return None
  else:
    Log(ERROR, 'Bad response')
    return None

def ParseSteamGame(app):
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
    game['price'] = PriceToFloat(app['price_overview']['final_formatted'])

  game['dlc_count'] = len(app['dlc']) if 'dlc' in app else 0
  game['detailed_description'] = app['detailed_description'].strip() if 'detailed_description' in app else ''
  game['about_the_game'] = app['about_the_game'].strip() if 'about_the_game' in app else ''
  game['short_description'] = app['short_description'].strip() if 'short_description' in app else ''
  game['reviews'] = app['reviews'].strip() if 'reviews' in app else ''
  game['header_image'] = app['header_image'].strip() if 'header_image' in app and app['header_image'] else ''
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
          subs.append({'text': SanitizeText(sub['option_text']),
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
      if 'mp4' in movie:
        game['movies'].append(movie['mp4']['max'])

  game['detailed_description'] = SanitizeText(game['detailed_description'])
  game['about_the_game'] = SanitizeText(game['about_the_game'])
  game['short_description'] = SanitizeText(game['short_description'])
  game['reviews'] = SanitizeText(game['reviews'])
  game['notes'] = SanitizeText(game['notes'])

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

def Scraper(dataset, notreleased, discarded, args, steam_api_key, appIDs = None):
  '''
  Search games in Steam.
  '''
  apps = []
  if appIDs is None:
    # Load existing applist if it exists
    if os.path.exists(APPLIST_FILE):
      with open(APPLIST_FILE, 'r', encoding='utf-8') as fin:
        text = fin.read()
        if len(text) > 0:
          apps = json.loads(text)
          Log(INFO, f'List with {len(apps)} games loaded from {APPLIST_FILE}')

    # Update from Steam if not explicitly disabled
    if args.only_applist == False:
      Log(INFO, 'Updating list of games from Steam')
      steam_apps = []
      last_appid = 0
      while True:
        parameters = {
          'key': steam_api_key,
          'max_results': 50000,
          'last_appid': last_appid
        }
        response = DoRequest('https://api.steampowered.com/IStoreService/GetAppList/v1/', parameters)
        if response:
          data = response.json()
          if 'response' in data and 'apps' in data['response']:
            batch = [str(x["appid"]) for x in data['response']['apps']]
            steam_apps.extend(batch)
            if data['response'].get('have_more_results'):
              last_appid = data['response'].get('last_appid')
              Log(INFO, f'Retrieved {len(steam_apps)} apps from Steam...')
              time.sleep(args.sleep)
            else:
              break
          else:
            Log(ERROR, 'Unexpected response format from Steam API')
            break
        else:
          break

      if steam_apps:
        # Merge and remove duplicates
        apps = list(set(apps + steam_apps))
        Log(INFO, f'List updated: {len(apps)} total games')
        with open(APPLIST_FILE, 'w', encoding='utf-8') as fout:
          fout.seek(0)
          fout.write(json.dumps(apps, indent=4, ensure_ascii=False))
          fout.truncate()
    elif not apps:
      Log(ERROR, f'{APPLIST_FILE} not found and --only-applist is enabled')
      sys.exit()
  else:
    apps = appIDs

  if apps:
    gamesAdded = 0
    gamesNotReleased = 0
    gamesDiscarded = 0
    successRequestCount = 0
    errorRequestCount = 0

    random.shuffle(apps)
    total = len(apps)
    count = 0

    try:
      for appID in apps:
        if appID not in dataset and appID not in discarded:
          if args.released and appID in notreleased:
            continue

          app, reason, name = SteamRequest(appID, min(4, args.sleep), successRequestCount, errorRequestCount, args.retries)
          if app:
            game = ParseSteamGame(app)
            if game['release_date'] != '':
              if args.steamspy:
                extra = SteamSpyRequest(appID, min(4, args.sleep), successRequestCount, errorRequestCount, args.retries)
                if extra != None:
                  game['user_score'] = extra['userscore']
                  game['score_rank'] = extra['score_rank']
                  game['positive'] = extra['positive']
                  game['negative'] = extra['negative']
                  game['estimated_owners'] = extra['owners'].replace(',', '').replace('..', '-')
                  game['average_playtime_forever'] = extra['average_forever']
                  game['average_playtime_2weeks'] = extra['average_2weeks']
                  game['median_playtime_forever'] = extra['median_forever']
                  game['median_playtime_2weeks'] = extra['median_2weeks']
                  game['discount'] = extra['discount']
                  game['peak_ccu'] = extra['ccu']
                  game['tags'] = extra['tags']
                else:
                  game['user_score'] = 0
                  game['score_rank'] = ""
                  game['positive'] = 0
                  game['negative'] = 0
                  game['estimated_owners'] = "0 - 0"
                  game['average_playtime_forever'] = 0
                  game['average_playtime_2weeks'] = 0
                  game['median_playtime_forever'] = 0
                  game['median_playtime_2weeks'] = 0
                  game['discount'] = 0
                  game['peak_ccu'] = 0
                  game['tags'] = []

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
            discarded[appID] = {'name': name, 'reason': reason}
            gamesDiscarded += 1

          if args.autosave > 0 and gamesDiscarded > 0 and gamesDiscarded % args.autosave == 0:
            SaveJSON(discarded, DISCARDED_FILE, True)

          time.sleep(args.sleep if random.random() > 0.1 else args.sleep * 2.0)
        count += 1
        ProgressBar('Scraping', count, total)
    except KeyboardInterrupt:
      pass

    ProgressBar('Scraping', total, total)
    print('\r')
    SaveJSON(dataset, args.outfile)
    SaveJSON(discarded, DISCARDED_FILE)
    SaveJSON(notreleased, NOTRELEASED_FILE)

    return gamesAdded, gamesNotReleased, gamesDiscarded

  return 0, 0, 0

def UpdateFromCSV(dataset, notreleased, discarded, args, steam_api_key):
  '''
  Update using APPIDs from a CSV file. The first column must contain the APPID.
  '''
  fieldSizeLimit = sys.maxsize
  while True:
    try:
      csv.field_size_limit(fieldSizeLimit)
      break
    except OverflowError:
      fieldSizeLimit = int(fieldSizeLimit / 2)

  if os.path.exists(args.update):
    Log(INFO, f"Loading '{args.update}'")
    appIDs = []
    with open(args.update, encoding='utf8') as csvFile:
      reader = csv.reader(csvFile, delimiter=',', quotechar='|')
      for row in reader:
        if len(row) > 0 and row[0].isnumeric():
          appID = row[0]
          if appID not in dataset and appID not in discarded and appID not in notreleased:
            appIDs.append(row[0])

    if len(appIDs) > 0:
      Log(INFO, f"New {len(appIDs)} appIDs loaded from '{args.update}'")

      return Scraper(dataset, notreleased, discarded, args, steam_api_key, appIDs)
    else:
      Log(WARNING, f'No appID loaded from {args.update}')
  else:
    Log(ERROR, f'File {args.update} not found')

  return 0, 0, 0

if __name__ == "__main__":
  Log(INFO, f'Steam Games Scraper {__version__} by {__author__}')
  parser = argparse.ArgumentParser(description='Steam games scraper.')
  parser.add_argument('-i', '--infile',   type=str,   default=DEFAULT_INFILE,  help='Input file name')
  parser.add_argument('-o', '--outfile',  type=str,   default=DEFAULT_OUTFILE,  help='Output file name')
  parser.add_argument('-s', '--sleep',    type=float, default=DEFAULT_SLEEP,    help='Waiting time between requests')
  parser.add_argument('-r', '--retries',  type=int,   default=DEFAULT_RETRIES,  help='Number of retries (0 to always retry)')
  parser.add_argument('-a', '--autosave', type=int,   default=DEFAULT_AUTOSAVE, help='Record the data every number of new entries (0 to deactivate)')
  parser.add_argument('-d', '--released', type=bool,  default=True,             help='If it is on the list of not yet released, no information is requested')
  parser.add_argument('-c', '--currency', type=str,   default=DEFAULT_CURRENCY, help='Currency code')
  parser.add_argument('-l', '--language', type=str,   default=DEFAULT_LANGUAGE, help='Language code')
  parser.add_argument('-p', '--steamspy', type=str,   default=True,             help='Add SteamSpy info')
  parser.add_argument('-u', '--update',   type=str,   default='',               help='Update using APPIDs from a CSV file')
  parser.add_argument('-oa', '--only-applist', action='store_true',             help='Only use the applist file, do not update it from Steam')
  args = parser.parse_args()
  random.seed(time.time())

  if 'h' in args or 'help' in args:
    parser.print_help()
    sys.exit()

  # Get the Steam API key from the .env file
  STEAM_API_KEY = None
  if os.path.exists('.env'):
    with open('.env', 'r') as f:
      for line in f:
        if line.startswith('STEAM_API_KEY='):
          STEAM_API_KEY = line.split('=')[1].strip()
          break
  else:
    Log(ERROR, 'STEAM_API_KEY not found in .env')
    sys.exit(1)

  if STEAM_API_KEY is None:
    Log(ERROR, 'STEAM_API_KEY not found in .env')
    Log(INFO, 'Create a .env file with the API key. You can get it from https://steamcommunity.com/dev/apikey')
    sys.exit(1)

  dataset = LoadJSON(args.infile)
  discarded = LoadJSON(DISCARDED_FILE)
  notreleased = LoadJSON(NOTRELEASED_FILE)

  if dataset is None:
    dataset = {}

  if discarded is None:
    discarded = {}
  elif isinstance(discarded, list):
    Log(INFO, f'Migrating {len(discarded)} discarded apps to new format')
    discarded = {appID: {'name': 'Unknown', 'reason': 'legacy'} for appID in discarded}

  if notreleased is None:
    notreleased = []

  Log(INFO, f'Dataset loaded with {len(dataset)} games' if len(dataset) > 0 else 'New dataset created')

  if len(notreleased) > 0:
    Log(INFO, f'{len(notreleased)} games not released yet')

  if len(discarded) > 0:
    Log(INFO, f'{len(discarded)} apps discarded')

  start_time = time.time()
  try:
    added, not_released, discarded_count = (0, 0, 0)
    if args.update == '':
      added, not_released, discarded_count = Scraper(dataset, notreleased, discarded, args, STEAM_API_KEY)
    else:
      added, not_released, discarded_count = UpdateFromCSV(dataset, notreleased, discarded, args, STEAM_API_KEY)
  except (KeyboardInterrupt, SystemExit):
    added, not_released, discarded_count = (0, 0, 0) # Fallback if error occurs before Scraper starts

  end_time = time.time()
  duration = end_time - start_time
  
  if added > 0 or not_released > 0 or discarded_count > 0:
    growth = (added / (len(dataset) - added) * 100) if (len(dataset) - added) > 0 else 100

    print('\n' + '='*50)
    print(f" SESSION STATISTICS")
    print('='*50)
    print(f" Time elapsed:    {time.strftime('%H:%M:%S', time.gmtime(duration))}")
    if added > 0:
      print(f" Avg time/game:   {duration/added:.2f}s")
    print(f" New games:       {added} (+{growth:.2f}% growth)")
    print(f" Not released:    {not_released}")
    print(f" Discarded:       {discarded_count}")
    print('-'*50)
    print(f" TOTAL DATABASE STATS")
    print('-'*50)
    print(f" Total games:     {len(dataset)}")
    print(f" Total discarded: {len(discarded)}")
    print(f" Total pending:   {len(notreleased)}")
    print('='*50 + '\n')

  SaveJSON(dataset, args.outfile, args.autosave > 0)
  SaveJSON(discarded, DISCARDED_FILE, args.autosave > 0)
  SaveJSON(notreleased, NOTRELEASED_FILE, args.autosave > 0)

  Log(INFO, 'Done')
