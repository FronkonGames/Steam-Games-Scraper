<p align="center"><img src="images/banner.png"/></p>
<br>

Extract information from all games published in Steam thanks to its [Web API](https://partner.steamgames.com/doc/webapi_overview), and store it in JSON format.

# 🔧 Requisites

- Pyhton 3.8
- argparse

# 🚀 Usage

Start generating data simply with:

```
python SteamGamesScraper.py
```

The first time you do, the file '_appplist.json_' will be created with all the ID that facilitates Steam (>140K). In the next execution, that file will be used instead of requesting all the data again. If you want to get new IDs, simply delete the file '_appplist.json_'.

Only the data of the games are saved. DLCs, music, tools, etc. are ignored and added to the file 'discarted.json' so as not to ask for them in future searches. The game IDs that Steam does not do us from information is also added. You can delete the file to ask again for those IDs.

Finally, in the file '_games.json'_ all games are stored that:

* It have been already been released.
* 'developers' field not empty.
* Price included if its not free.

The format is this:

```
{
    "906850": {
        "name": "Game Name",
        "release_date": {
            "coming_soon": false,
            "date": "8 Aug, 2018"
        },
        "required_age": 0,
        "is_free": false,
        "price": "3,99€",
        "detailed_description": "...",
        "supported_languages": "English",
        "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/906850/header.jpg?t=1629556612",
        "website": "",
        "developers": [
            "KillGame"
        ],
        "publishers": [
            "HandMade Games"
        ],
        "windows": false,
        "mac": false,
        "linux": false,
        "categories": [
            "Single-player"
        ],
        "genres": [
            "Indie"
        ],
        "screenshots": [
            "https://cdn.akamai.steamstatic.com/steam/apps/906850/ss_771b01cae86ac9ab0ba9b2e14f27ec8d8d04e3ae.1920x1080.jpg?t=1629556612",
            "https://cdn.akamai.steamstatic.com/steam/apps/906850/ss_cbae6cabaaeff0ab297514dd6b7bf3231702f4eb.1920x1080.jpg?t=1629556612"
        ],
        "movies": [
            "http://cdn.akamai.steamstatic.com/steam/apps/256722964/movie_max.mp4?t=1532169660"
        ],
        "achievements": 0
    },
    ...
}
```

To change the output file uses the parameter '_-o_' / '_-outfile_':

```
python SteamGamesScraper.py -o output.json
```

Steam can reject, or even banner your IP, if he considers that you are doing too many requests. That's why 1.5 seconds are waited by default. You can change this with the parameter '_-s_' / '_-sleep_':

```
python SteamGamesScraper.py -s 0.5
```

> **It is not recommended to download the waiting time of 1.5 seconds.**

When Steam denies a request, by default it is trying up to four times. Puedes cambiar el numero de reintentos con '_-r_' / '_-retries_':

```
python SteamGamesScraper.py -r 10
```

> **Although it is not recommended, you can always retry by changing the value to 0.**


## 📜 License

Code released under [MIT License](https://github.com/FronkonGames/Machine-Learning-Game-Ideas/blob/main/LICENSE.md).
