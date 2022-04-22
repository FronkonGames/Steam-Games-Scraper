
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
import argparse
from ssl import SSLError
import requests
import json
import time
from os.path import exists
import traceback

APPLIST_FILE    = 'applist.json'
OUT_FILE        = 'games.json'
DISCARTED_FILE  = 'discarted.json'

def DoRequest(url, parameters=None, retryTime=4, successCount=0, errorCount=0, retries=0):
  response = None
  try:
    response = requests.get(url=url, params=parameters)
  except SSLError as e:
    print(f'[!!] {e}.')
    response = None

  if response and response.status_code == 200:
    errorCount = 0
    successCount += 1
    if successCount > retryTime:
      retryTime = min(4, retryTime / 2)
      successCount = 0
  elif retries > 0:
    if errorCount < retries:
      print(f'[W] {response.reason}, retrying in {retryTime} seconds.')
      errorCount += 1
      successCount = 0
      time.sleep(retryTime)
      retryTime = min(retryTime * 2, 256)
      return DoRequest(url, parameters, retryTime, successCount, errorCount, retries)
    else:
      print('[!!] Number of retries expired.')
      sys.exit()

  return response

def ParseSteamRequest(appID, retryTime, successRequestCount, errorRequestCount, retries):
  url = "http://store.steampowered.com/api/appdetails/"
  response = DoRequest(url, {"appids": appID}, retryTime, successRequestCount, errorRequestCount, retries)
  if response:
    try:
      data = response.json()
      app = data[appID]
      if app['success'] == False:
        print(f'[w] \'{appID}\' info not available.')
        return None
      elif app['data']['type'] != 'game':
        type = app['data']['type']
        print(f'[w] \'{appID}\' is not a game ({type}).')
        return None
      elif app['data']['is_free'] == False and 'price_overview' in app['data'] and app['data']['price_overview']['final_formatted'] == '':
        print(f'[w] \'{appID}\' is not free but has no price.')
        return None
      elif 'developers' in app['data'] and len(app['data']['developers']) == 0:
        print(f'[w] \'{appID}\' has no developers.')
        return None
      elif app['data']['release_date']['coming_soon'] == True:
        print(f'[w] \'{appID}\' is not released yet.')
        return None
      else:
        return app['data']
    except:
      print(f'[!!] {traceback.format_exc()}')
      return None
  else:
    print('[!] Bad response.')
    return None

def LoadDataset(args):
  dataset = {}
  try:
    if exists(args.outfile):
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
  except:
    print(f'[!!] {traceback.format_exc()}')
    sys.exit()

def LoadDiscarted():
  discarted = []
  try:
    if exists(DISCARTED_FILE):
      with open(DISCARTED_FILE, 'r', encoding='utf-8') as fin:
        text = fin.read()
        if len(text) > 0:
          discarted = json.loads(text)
          print(f'[i] {len(discarted)} games discarted.')

    return discarted
  except:
    print(f'[!!] {traceback.format_exc()}')
    sys.exit()

def SaveDataset(dataset, args):
  try:
    with open(args.outfile, 'w', encoding='utf-8') as fout:
      fout.seek(0)
      fout.write(json.dumps(dataset, indent=4, ensure_ascii=False))
      fout.truncate()
  except:
    print(f'[!!] {traceback.format_exc()}')
    sys.exit()

def SaveDiscarted(discarted):
  try:
    with open(DISCARTED_FILE, 'w', encoding='utf-8') as fout:
      fout.seek(0)
      fout.write(json.dumps(discarted, indent=4, ensure_ascii=False))
      fout.truncate()
  except:
    print(f'[!!] {traceback.format_exc()}')
    sys.exit()

def Scraper(dataset, discarted, args):
  apps = []
  if exists(APPLIST_FILE):
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
    print(f'[i] Scanning {len(apps) - len(discarted)} games (CTRL+C to exit).')
    gamesAdded = 0
    gamesDiscarted = 0
    retryTime = 4
    successRequestCount = 0
    errorRequestCount = 0

    for appID in apps:
      if appID not in dataset and appID not in discarted:
        app = ParseSteamRequest(appID, retryTime, successRequestCount, errorRequestCount, args.retries)
        if app:
          name = app['name'].strip()

          release_date = app['release_date'] if 'release_date' in app and not app['release_date']['coming_soon'] else ''
          required_age = int(app['required_age']) if 'required_age' in app else 0
          is_free = app['is_free']
          price = app['price_overview']['final_formatted'] if 'price_overview' in app else ''
          detailed_description = app['detailed_description'].strip() if 'detailed_description' in app else ''
          about_the_game = app['about_the_game'].strip() if 'about_the_game' in app else ''
          short_description = app['short_description'].strip() if 'short_description' in app else ''
          supported_languages = app['supported_languages'] if 'supported_languages' in app else ''
          header_image = app['header_image'].strip() if 'header_image' in app else ''
          website = app['website'].strip() if 'website' in app and app['website'] is not None else ''

          developers = []
          if 'developers' in app:
            for developer in app['developers']:
              developers.append(developer.strip())

          publishers = []
          if 'publishers' in app:
            for publisher in app['publishers']:
              publishers.append(publisher.strip())

          windows = True if app['platforms']['windows'] == 'true' else False
          mac = True if app['platforms']['mac'] == 'true' else False
          linux = True if app['platforms']['linux'] == 'true' else False

          categories = []
          if 'categories' in app:
            for category in app['categories']:
              categories.append(category['description'])

          genres = []
          if 'genres' in app:
            for genre in app['genres']:
              genres.append(genre['description'])

          screenshots = []
          if 'screenshots' in app:
            for screenshot in app['screenshots']:
              screenshots.append(screenshot['path_full'])

          movies = []
          if 'movies' in app:
            for movie in app['movies']:
              movies.append(movie['mp4']['max'])

          achievements = int(app['achievements']['total']) if 'achievements' in app else 0

          dataset[appID] = {}
          dataset[appID]['name'] = name
          dataset[appID]['release_date'] = release_date
          dataset[appID]['required_age'] = required_age
          dataset[appID]['is_free'] = is_free
          dataset[appID]['price'] = price
          dataset[appID]['detailed_description'] = detailed_description
          dataset[appID]['about_the_game'] = about_the_game
          dataset[appID]['short_description'] = short_description
          dataset[appID]['supported_languages'] = supported_languages
          dataset[appID]['header_image'] = header_image
          dataset[appID]['website'] = website
          dataset[appID]['developers'] = developers
          dataset[appID]['publishers'] = publishers
          dataset[appID]['windows'] = windows
          dataset[appID]['mac'] = mac
          dataset[appID]['linux'] = linux
          dataset[appID]['categories'] = categories
          dataset[appID]['genres'] = genres
          dataset[appID]['screenshots'] = screenshots
          dataset[appID]['movies'] = movies
          dataset[appID]['achievements'] = achievements

          print(f'[i] Game \'{name}\' added ({len(dataset)}).')

          gamesAdded += 1
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
  parser = argparse.ArgumentParser(description='Steam games scraper.')
  parser.add_argument('-o', '--outfile', type=str, default=OUT_FILE, help='Output file name')
  parser.add_argument('-s', '--sleep', type=float, default=1.5, help='Waiting time between requests')
  parser.add_argument('-r', '--retries', type=int, default=4, help='Number of retries (0 to always retry)')
  args = parser.parse_args()

  if 'h' in args or 'help' in args:
    parser.print_help()
    sys.exit()

  dataset = LoadDataset(args)
  discarted = LoadDiscarted()

  try:
    Scraper(dataset, discarted, args)
  except (KeyboardInterrupt, SystemExit):
    SaveDataset(dataset, args)
    SaveDiscarted(discarted)
    print('[i] Done.')
