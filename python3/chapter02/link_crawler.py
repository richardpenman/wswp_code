import urllib.robotparser
from urllib.parse import urljoin, urlparse, urldefrag
from datetime import datetime
import time
import urllib3
import re


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1,
                 headers=None, user_agent='wswp3', proxy=None, num_retries=1,
                 scrape_callback=None):
    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, headers, proxy, num_retries)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])
            if depth != max_depth:
                if link_regex:
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))
                for link in links:
                    link = normalize(seed_url, link)
                    if link not in seen:
                        seen[link] = depth + 1
                        if same_domain(seed_url, link):
                            crawl_queue.append(link)
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print('Blocked by robots.txt:', url)


class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


def download(url, headers, proxy, num_retries):
    print('Downloading:', url)
    if proxy:
        http = urllib3.ProxyManager(proxy, headers=headers)
    else:
        http = urllib3.PoolManager(headers=headers)
    try:
        response = http.request('get', url)
        html = response.data
        if num_retries > 0 and hasattr(response, 'status') and 500 <= response.status < 600:
            html = download(url, headers, proxy, num_retries - 1)
    except urllib3.exceptions.MaxRetryError as e:
        print('Download error:', e.reason)
        html = None
    if isinstance(html, bytes):
        return html.decode('utf-8')
    else:
        return html


def normalize(seed_url, link):
    link, _ = urldefrag(link)
    return urljoin(seed_url, link)


def same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc


def get_robots(url):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    rp.read()
    return rp


def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/places/default/(index|view)',
                 delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/places/default/(index|view)',
                 delay=0, num_retries=1, max_depth=1, user_agent='GoodCrawler')
