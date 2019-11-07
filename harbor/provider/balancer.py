import time
from collections import defaultdict
from urllib.parse import urlparse


from typing import TYPE_CHECKING

import requests

from harbor import conf
from harbor import logger

if TYPE_CHECKING:
    from requests import Response


class RequestStat:
    def __init__(self):
        self.last_request_dts = None
        self.count = 0


class AntiSpamRequestBalancer:
    def __init__(self):
        self.hosts = defaultdict(int)
        self.max_requests = conf.MAX_REQUEST_RATE
        self.delay_sec = conf.REQUESTS_DELAY_SEC

    def get(self, url: str, params: dict = None) -> 'Response':
        host = urlparse(url).hostname
        count = self.hosts[host]
        if count > self.max_requests:
            self.hosts[host] = 0
            logger.info(f"rate limit for {host} is exceeded")
            time.sleep(self.delay_sec)

        self.hosts[host] += 1

        return requests.get(url, params)


requester = AntiSpamRequestBalancer()
