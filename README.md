# pyharbor
Telegram bot that notifies about new property offers in Kyiv
The purpose of Bot is to publish data into private chat with other participants, that cause of hart to configure it. 
Еhe service is intended for personal use only.

## Algorithm
One in a period job pulls out property items from particular site from config.json. 
The items store in sqlite. After each pulling runs separate thead to publish offers in Telegram's private chat.
User can choose two options: Dislike - the offer will be removed and never posted; or Like - just save in history :)

## Implementation
1. [https://github.com/pyenv/pyenv](pyenv) & [https://github.com/pypa/pipenv](pipenv)
2. [https://www.sqlite.org/index.html](SQLite)

## Configuration
1. Make a copy of `config.json.example` and name it as `config.json`

```
{
  "app": {
    "update_frequency": 30,     # each N seconds run a job for pulling data
    "max_request_rate": 5,      # anti-spam feature; do not allow more than 5 requests
    "requests_delay": 3,        # delay is secs after max_request_rate exceeded
    "telegram_api_token": "_api_token_",  # your Telegram Bot token, can be created via @botfather
    "telegram_chat_id": "@chat_name"  # your chat id. Note that @chat_name notation is for public chats. You must specify int value for private ones
  },
  "providers": [
      {
        "name": "rieltor",  # proivder name, currenly only supported
        "base_url": "https://rieltor.ua/flats-sale/",  # provider base url
        "filter": {  # pull filters
            "max_items_to_load": 25,  # max items to load
            "max_images_to_load": 3,  # each item has a photos; no need to pull them all; 
            "locations": [            # preferd locations, see pyharbor.provider.rieltor.locations.Location for details
                "Оболонський": 76
            ],
            "price_min": 50000,
            "price_max": 65000,
            "rooms": [2],
            "min_square": 50
        }
      }
  ]
}
```
2. Set env variable `HARBOR_ROOT=<dir where config.json are placed>`

## Run
`python cli.py run`

Tested on Windows env only
