<p align="center"><img src="images/banner.png"/></p>
<br>

Extract information from all games published in Steam thanks to its [Web API](https://partner.steamgames.com/doc/webapi_overview), and store it in JSON format. It also collects extra data from [SteamSpy](https://steamspy.com/).

I used this code to generate these dataset: '[Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset)'.

# Requisites 🔧

- Pyhton 3.8
- requests and argparse.

```
pip3 install requests argparse
```

# Steam API Key 🔑

The original public endpoint for retrieving the app list has been deprecated by Steam. The new official method via the `IStoreService` requires a valid Steam API Key.

1. Get your API Key from the [Steam Community Dev page](https://steamcommunity.com/dev/apikey).
2. Create a file named `.env` in the root directory of this project.
3. Add your key to the file like this:
   ```
   STEAM_API_KEY=YOUR_KEY_HERE
   ```

# Usage 🚀

Start generating data simply with:

```
python SteamGamesScraper.py
```

The first time, the file `applist.json` will be created with all the IDs provided by Steam (>140K). This requires the `STEAM_API_KEY` to be set in your `.env` file. In subsequent executions, the script will load the existing `applist.json` and update it with any new IDs found on Steam.

If you want to skip the update and only use the local `applist.json` file, use the `-oa` / `--only-applist` parameter.

Only the data of the games are saved. DLCs, music, tools, etc. are ignored and added to the file `discarted.json` so as not to ask for them in future searches. You can delete the file to ask again for those IDs.

Finally, in the file '_games.json'_ all games are stored, if:

* It have been already been released.
* 'developers' field not empty.
* Price included if its not free.

The format is this:

```
{
    "906850": {
        "name": "...",
        "release_date": {
            "coming_soon": false,
            "date": "..."
        },
        "required_age": 0,
        "is_free": false,
        "price": 0.99,
        "detailed_description": "...",
        "supported_languages": "...",
        "reviews": "...",
        "header_image": "...",
        "website": "...",
        "support_url": "...",
        "support_email": "...",
        "windows": true,
        "mac": false,
        "linux": false,
        "metacritic_score": 0,
        "metacritic_url": "...",
        "achievements": 0,
        "recommendations": 0,
        "notes": "",
        "packages": [
            {
                "title": "...",
                "description": "...",
                "subs": [
                    {
                        "text": "...",
                        "description": "...",
                        "price": 0.99
                    }
                ]
            }
        ],
        "developers": [
            "..."
        ],
        "publishers": [
            "..."
        ],
        "categories": [
            "..."
        ],
        "genres": [
            "..."
        ],
        "screenshots": [
            "..."
        ],
        "movies": [
            "..."
        ],
        "user_score": 0,
        "score_rank": "",
        "negative": 0,
        "positive": 1,
        "estimated_owners": "0 - 20000",
        "average_playtime_forever": 0,
        "average_playtime_2weeks": 0,
        "median_playtime_forever": 0,
        "median_playtime_2weeks": 0,
        "peak_ccu": 0,
        "tags": {
            "...": 22,
            ...
        }
    },
    ...
}
```

In the file '_ParseExample.py_' you can see a simple example of how to parse the information.

# ⚙️ Parameters

To change the input file uses the parameter '_-i_' / '_-infile_':

```
python SteamGamesScraper.py -i games.json
```

To change the output file uses the parameter '_-o_' / '_-outfile_':

```
python SteamGamesScraper.py -o output.json
```

There is a general API rate limit for each unique IP adress of 200 requests in five minutes which is one request every 1.5 seconds. That's why 1.5 seconds are waited by default. You can change this with the parameter '_-s_' / '_-sleep_':

```
python SteamGamesScraper.py -s 2.0
```

> **It is not recommended to set the wait time below 1.5 seconds.**

You can disable the extra data collected in SteamSpy using '_-p_' / '_-steamspy'_:

```
python SteamGamesScraper.py -p False
```

> **When this option is deactivated, some data will appear as empty.**

When Steam denies a request, by default it is trying up to four times. You can change the number of retries with '_-r_' / '_-retries_':

```
python SteamGamesScraper.py -r 10
```

> **Although it is not recommended, you can set always retry by changing the value to 0.**

By default prices are requested in US dollars. You can change the currency with the parameter '_-c_' / '_--currency_' and the country or region code:

```
python SteamGamesScraper.py -c es
```

By default the language is set to English. You can change the language wit the parameter '_-l_' / '_--language_' and the country or region code:

```
python SteamGamesScraper.py -l en
```

The games that have not yet been released are added to the file '_notreleased.json_' and will not be checked again. If you want to ignore this list, you can set the parameter '_-d_' / '_-released_' to _False_, or eliminate the file.

At the end of the scan, or by pressing _Ctrl + C_, all data are recorded. You can activate the _auto-save_ to activate each X new entries with '_-a_' / '_-autosave_':

```
python SteamGamesScraper.py -a 100
```

> A backup file will also be generated with the previous data.

Do you want to add new games from a file? You can use the parameter '_-u_' / '_-update_' and the CSV file name to add new games. The AppID must be in the first column.

```
python SteamGamesScraper.py -u update.csv
```

To only use the local `applist.json` file and skip checking for new games from Steam, use the parameter `-oa` / `--only-applist`:

```
python SteamGamesScraper.py -oa
```


## Contributors ✨

[![](https://github.com/DanielSchimit.png?size=75)](https://github.com/DanielSchimit)
[![](https://github.com/xArkqngel.png?size=75)](https://github.com/xArkqngel)

## License 📜

Code released under [MIT License](https://github.com/FronkonGames/Machine-Learning-Game-Ideas/blob/main/LICENSE.md).
