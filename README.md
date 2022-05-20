<p align="center"><img src="images/banner.png"/></p>
<br>

Extract information from all games published in Steam thanks to its [Web API](https://partner.steamgames.com/doc/webapi_overview), and store it in JSON format.

I used this code to generate these dataset: '[Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset)'.

# 🔧 Requisites

- Pyhton 3.8
- requests and argparse.

```
pip3 install requests argparse
```

# 🚀 Usage

Start generating data simply with:

```
python SteamGamesScraper.py
```

The first time, the file '_appplist.json_' will be created with all the ID that facilitates Steam (>140K). In the next execution, that file will be used instead of requesting all the data again. If you want to get new IDs, simply delete the file '_appplist.json_'.

Only the data of the games are saved. DLCs, music, tools, etc. are ignored and added to the file '_discarted.json_' so as not to ask for them in future searches. You can delete the file to ask again for those IDs.

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
        ]
    },
    ...
}
```

In the file '_ParseExample.py_' you can see a simple example of how to parse the information.

# ⚙️ Parameters

To change the output file uses the parameter '_-o_' / '_-outfile_':

```
python SteamGamesScraper.py -o output.json
```

Steam can reject, or even banner your IP, if he considers that you are doing too many requests. That's why 4.0 seconds are waited by default. You can change this with the parameter '_-s_' / '_-sleep_':

```
python SteamGamesScraper.py -s 2.0
```

> **It is not recommended to set the wait time below 4.0 seconds.**

When Steam denies a request, by default it is trying up to four times. You can change the number of retries with '_-r_' / '_-retries_':

```
python SteamGamesScraper.py -r 10
```

> **Although it is not recommended, you can set always retry by changing the value to 0.**

The games that have not yet been released are added to the file '_notreleased.json_' and will not be checked again. If you want to ignore this list, you can set the parameter '_-d_' / '_-released_' to _False_, or eliminate the file.

At the end of the scan, or by pressing _Ctrl + C_, all data are recorded. You can activate the _auto-save_ to activate each X new entries with '_-a_' / '_-autosave_':

```
python SteamGamesScraper.py -a 100
```

> A backup file will also be generated with the previous data.

## 📜 License

Code released under [MIT License](https://github.com/FronkonGames/Machine-Learning-Game-Ideas/blob/main/LICENSE.md).
