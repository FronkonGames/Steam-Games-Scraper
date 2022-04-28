
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
from ssl import SSLError
import requests
import json
import time
import traceback
import argparse

DEFAULT_OUTFILE  = 'games.json'
APPLIST_FILE     = 'applist.json'
DISCARTED_FILE   = 'discarted.json'
DEFAULT_SLEEP    = 1.5
DEFAULT_RETRIES  = 4
DEFAULT_AUTOSAVE = 100
DEFAULT_TIMEOUT  = 5
DEFAULT_CURRENCY = 'us'

def DoRequest(url, parameters=None, retryTime=4, successCount=0, errorCount=0, retries=0):
  '''
  Makes a Web request. If an error occurs, retry.
  '''
  response = None
  try:
    response = requests.get(url=url, params=parameters, timeout=DEFAULT_TIMEOUT)
  except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
          requests.exceptions.Timeout, requests.exceptions.RequestException,
          SSLError) as ex:
    print(f'[!!] An exception of type {type(ex).__name__} ocurred. Traceback: {traceback.format_exc()}')
    response = None

  if response and response.status_code == 200:
    errorCount = 0
    successCount += 1
    if successCount > retryTime:
      retryTime = min(4, retryTime / 2)
      successCount = 0
  else:
    if retries == 0 or errorCount < retries:
      if response is not None:
        print(f'[W] {response.reason}, retrying in {retryTime} seconds.')
      else:
        print(f'[W] Request failed, retrying in {retryTime} seconds.')
      errorCount += 1
      successCount = 0
      time.sleep(retryTime)
      retryTime = min(retryTime * 2, 256)
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
        print(f'[w] \'{appID}\' detail not available.')
        return None
      elif app['data']['type'] != 'game':
        type = app['data']['type']
        print(f'[i] \'{appID}\' is not a game ({type}).')
        return None
      elif app['data']['is_free'] == False and 'price_overview' in app['data'] and app['data']['price_overview']['final_formatted'] == '':
        print(f'[w] \'{appID}\' is not free but has no price.')
        return None
      elif 'developers' in app['data'] and len(app['data']['developers']) == 0:
        print(f'[w] \'{appID}\' has no developers.')
        return None
      elif app['data']['release_date']['coming_soon'] == True:
        print(f'[i] \'{appID}\' is not released yet.')
        return None
      else:
        return app['data']
    except Exception as ex:
      print(f'[!!] An exception of type {type(ex).__name__} ocurred. Traceback: {traceback.format_exc()}')
      return None
  else:
    print('[!] Bad response.')
    return None

def ParseGame(app):
  '''
  Parse game info.
  '''
  game = {}
  game['name'] = app['name'].strip()
  game['release_date'] = app['release_date'] if 'release_date' in app and not app['release_date']['coming_soon'] else ''
  game['required_age'] = int(str(app['required_age']).replace('+', '')) if 'required_age' in app else 0
  game['is_free'] = app['is_free']
  game['price'] = app['price_overview']['final_formatted'] if 'price_overview' in app else ''
  game['detailed_description'] = app['detailed_description'].strip() if 'detailed_description' in app else ''
  game['about_the_game'] = app['about_the_game'].strip() if 'about_the_game' in app else ''
  game['short_description'] = app['short_description'].strip() if 'short_description' in app else ''
  game['supported_languages'] = app['supported_languages'] if 'supported_languages' in app else ''
  game['header_image'] = app['header_image'].strip() if 'header_image' in app else ''
  game['website'] = app['website'].strip() if 'website' in app and app['website'] is not None else ''
  game['windows'] = True if app['platforms']['windows'] else False
  game['mac'] = True if app['platforms']['mac'] else False
  game['linux'] = True if app['platforms']['linux'] else False
  game['metacritic_score'] = str(app['metacritic']['score']) if 'metacritic' in app else ''
  game['metacritic_url'] = app['metacritic']['url'] if 'metacritic' in app else ''
  game['achievements'] = int(app['achievements']['total']) if 'achievements' in app else 0
  game['recommendations'] = app['recommendations']['total'] if 'recommendations' in app else 0
  game['notes'] = app['content_descriptors']['notes'] if 'content_descriptors' in app else ''

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

def LoadDataset(args):
  '''
  Load the dataset file.
  '''
  dataset = {}
  try:
    if os.path.exists(args.outfile):
      with open(args.outfile, 'r', encoding='utf-8') as fin:
        text = fin.read()
        if len(text) > 0:
          dataset = json.loads(text)
          print(f'[i] Dataset loaded with {len(dataset)} games.')
        else:
          print('[i] New dataset created.')
    else:
      print('[i] New dataset created.')

    return dataset
  except Exception as ex:
    print(f'[!!] An exception of type {type(ex).__name__} ocurred. Traceback: {traceback.format_exc()}')
    sys.exit()

def LoadDiscarted():
  '''
  Load a file with discarded apps.
  '''
  discarted = []
  try:
    if os.path.exists(DISCARTED_FILE):
      with open(DISCARTED_FILE, 'r', encoding='utf-8') as fin:
        text = fin.read()
        if len(text) > 0:
          discarted = json.loads(text)
          print(f'[i] {len(discarted)} apps discarted.')

    return discarted
  except Exception as ex:
    print(f'[!!] An exception of type {type(ex).__name__} ocurred. Traceback: {traceback.format_exc()}')
    sys.exit()

def SaveDataset(dataset, args):
  try:
    with open(args.outfile, 'w', encoding='utf-8') as fout:
      fout.seek(0)
      fout.write(json.dumps(dataset, indent=4, ensure_ascii=False))
      fout.truncate()
  except Exception as ex:
    print(f'[!!] An exception of type {type(ex).__name__} ocurred. Traceback: {traceback.format_exc()}')
    sys.exit()

def SaveDiscarted(discarted):
  '''
  Record all discarded apps in a file.
  '''
  try:
    with open(DISCARTED_FILE, 'w', encoding='utf-8') as fout:
      fout.seek(0)
      fout.write(json.dumps(discarted, indent=4, ensure_ascii=False))
      fout.truncate()
  except Exception as ex:
    print(f'[!!] An exception of type {type(ex).__name__} ocurred. Traceback: {traceback.format_exc()}')
    sys.exit()

def Scraper(dataset, discarted, args):
  '''
  Search games in Steam.
  '''
  apps = []
  if os.path.exists(APPLIST_FILE):
    with open(APPLIST_FILE, 'r', encoding='utf-8') as fin:
      text = fin.read()
      if len(text) > 0:
        apps = json.loads(text)
        print(f'[i] List with {len(apps)} games loaded.')
  else:
    print('[i] Requesting list of games from Steam.')
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
    print(f'[i] Scanning {len(apps) - len(discarted)} apps (CTRL+C to exit).')
    gamesAdded = 0
    gamesDiscarted = 0
    retryTime = 4
    successRequestCount = 0
    errorRequestCount = 0

    for appID in apps:
      if appID not in dataset and appID not in discarted:
        app = SteamRequest(appID, retryTime, successRequestCount, errorRequestCount, args.retries)
        if app:
          dataset[appID] = ParseGame(app)

          print(f"[i] '{dataset[appID]['name']}' added (#{len(dataset)}).")

          gamesAdded += 1

          if args.autosave > 0 and (gamesAdded + gamesDiscarted) % args.autosave == 0:
            print('[i] Autosaving.')
            SaveDataset(dataset, args)
            SaveDiscarted(discarted)
        else:
          discarted.append(appID)
          gamesDiscarted += 1

        time.sleep(args.sleep)

    SaveDataset(dataset)
    SaveDiscarted(discarted)
    print(f'[i] {gamesAdded} new games added, {gamesDiscarted} discarted.')
  else:
    print('[!!] Error requesting list of games.')
    sys.exit()

if __name__ == "__main__":
  print(f'[i] Steam Games Scraper {__version__} by {__author__}.')
  parser = argparse.ArgumentParser(description='Steam games scraper.')
  parser.add_argument('-o', '--outfile',  type=str,   default=DEFAULT_OUTFILE,  help='Output file name')
  parser.add_argument('-s', '--sleep',    type=float, default=DEFAULT_SLEEP,    help='Waiting time between requests')
  parser.add_argument('-r', '--retries',  type=int,   default=DEFAULT_RETRIES,  help='Number of retries (0 to always retry)')
  parser.add_argument('-a', '--autosave', type=int,   default=DEFAULT_AUTOSAVE, help='Record the data every number of new entries (0 to deactivate)')
  parser.add_argument('-c', '--currency', type=str,   default=DEFAULT_CURRENCY, help='Currency code')
  args = parser.parse_args()

  if 'h' in args or 'help' in args:
    parser.print_help()
    sys.exit()

  dataset = LoadDataset(args)

  try:
    discarted = LoadDiscarted()
    Scraper(dataset, discarted, args)
  except (KeyboardInterrupt, SystemExit):
    SaveDataset(dataset, args)
    SaveDiscarted(discarted)
    print('[i] Done.')
