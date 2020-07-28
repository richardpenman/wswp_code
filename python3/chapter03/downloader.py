from urllib.parse import urlsplit
from datetime import datetime
import time
import urllib3
import socket
import random

DEFAULT_AGENT = 'wswp3'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60


class Downloader:
    def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None,
                 num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, cache=None):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    result = None
        if result is None:
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, proxy, self.num_retries)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxy, num_retries):
        print('Downloading:', url)
        if proxy:
            http = urllib3.ProxyManager(proxy, headers=headers)
        else:
            http = urllib3.PoolManager(headers=headers)
        code = -1
        try:
            response = http.request('get', url)
            html = response.data
            if isinstance(html, bytes):
                html = html.decode('utf-8')
            code = response.status if hasattr(response, 'status') else -1
            if num_retries > 0 and 500 <= code < 600:
                return self.download(url, headers, proxy, num_retries - 1)
        except urllib3.exceptions.MaxRetryError as e:
            print('Download error:', e.reason)
            html = ''
        return {'html': html, 'code': code}


class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()
