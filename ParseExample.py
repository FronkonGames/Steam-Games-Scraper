# Simple parse of the 'games.json' file.
import os
import json

dataset = {}
if os.path.exists('games.json'):
  with open('games.json', 'r', encoding='utf-8') as fin:
    text = fin.read()
    if len(text) > 0:
      dataset = json.loads(text)

for app in dataset:
  appID = app                                         # AppID, unique identifier for each app (string).
  game = dataset[app]             

  name = game['name']                                 # Game name (string).
  releaseDate = game['release_date']                  # Release date (string).
  estimatedOwners = game['estimated_owners']          # Estimated owners (string, e.g.: "0 - 20000").
  peakCCU = game['peak_ccu']                          # Number of concurrent users, yesterday (int).
  required_age = game['required_age']                 # Age required to play, 0 if it is for all audiences (int).
  price = game['price']                               # Price in USD, 0.0 if its free (float).
  dlcCount = game['dlc_count']                        # Number of DLCs, 0 if you have none (int).
  longDesc = game['detailed_description']             # Detailed description of the game (string).
  shortDesc = game['short_description']               # Brief description of the game,
                                                      # does not contain HTML tags (string).
  languages = game['supported_languages']             # Comma-separated enumeration of supporting languages.
  fullAudioLanguages = game['full_audio_languages']   # Comma-separated enumeration of languages with audio support.
  reviews = game['reviews']                           #
  headerImage = game['header_image']                  # Header image URL in the store (string).
  website = game['website']                           # Game website (string).
  supportWeb = game['support_url']                    # Game support URL (string).
  supportEmail = game['support_email']                # Game support email (string).
  supportWindows = game['windows']                    # Does it support Windows? (bool).
  supportMac = game['mac']                            # Does it support Mac? (bool).
  supportLinux = game['linux']                        # Does it support Linux? (bool).
  metacriticScore = game['metacritic_score']          # Metacritic score, 0 if it has none (int).
  metacriticURL = game['metacritic_url']              # Metacritic review URL (string).
  userScore = game['user_score']                      # Users score, 0 if it has none (int).
  positive = game['positive']                         # Positive votes (int).
  negative = game['negative']                         # Negative votes (int).
  scoreRank = game['score_rank']                      # Score rank of the game based on user reviews (string).
  achievements = game['achievements']                 # Number of achievements, 0 if it has none (int).
  recommens = game['recommendations']                 # User recommendations, 0 if it has none (int).
  notes = game['notes']                               # Extra information about the game content (string).
  averagePlaytime = game['average_playtime_forever']  # Average playtime since March 2009, in minutes (int).
  averageplaytime2W = game['average_playtime_2weeks'] # Average playtime in the last two weeks, in minutes (int).
  medianPlaytime = game['median_playtime_forever']    # Median playtime since March 2009, in minutes (int).
  medianPlaytime2W = game['median_playtime_2weeks']   # Median playtime in the last two weeks, in minutes (int).

  packages = game['packages']                         # Available packages.
  for pack in packages:           
    title = pack['title']                             # Package title (string).
    packDesc = pack['description']                    # Package description (string).

    subs = pack['subs']                               # Subpackages.
    for sub in subs:            
      text = sub['text']                              # Subpackage title (string).
      subDesc = sub['description']                    # Subpackage description (string).
      subPrice = sub['price']                         # Subpackage price in USD (float).

  developers = game['developers']                     # Game developers.
  for developer in developers:            
    developerName = developer                         # Developer name (string).

  publishers = game['publishers']                     # Game publishers.
  for publisher in publishers:            
    publisherName = publisher                         # Publisher name (string).

  categories = game['categories']                     # Game categories.
  for category in categories:           
    categoryName = category                           # Category name (string).

  genres = game['genres']                             # Game genres.
  for gender in genres:           
    genderName = gender                               # Gender name (string).

  screenshots = game['scrennshots']                   # Game screenshots.
  for screenshot in screenshots:            
    scrennshotsURL = screenshot                       # Game screenshot URL (string).

  movies = game['movies']                             # Game movies.
  for movie in movies:            
    movieURL = movie                                  # Game movie URL (string).

  tags = game['tags']                                 # Tags.
  for tag in tags:           
    tagKey = tag                                      # Tag key (string, int).
