import time
from collections import defaultdict
from urllib.parse import urlparse


from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from requests import Response


class RequestStat:
    def __init__(self):
        self.last_request_dts = None
        self.count = 0


class AntiSpamRequestBalancer:
    def __init__(self):
        self.hosts = defaultdict(int)
        self.max_requests = 5
        self.delay_sec = 3

    def get(self, url: str, params: dict = None) -> 'Response':
        host = urlparse(url).hostname
        count = self.hosts[host]
        if count > self.max_requests:
            self.hosts[host] = 0
            time.sleep(self.delay_sec)

        self.hosts[host] += 1

        return requests.get(url, params)


requester = AntiSpamRequestBalancer()
