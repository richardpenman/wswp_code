# -*- coding: utf-8 -*-

from link_crawler import link_crawler
from mongo_cache import MongoCache
from alexa import AlexaCallback


def main():
    scrape_callback = AlexaCallback()
    cache = MongoCache()
    #cache.clear()
    #XXX zipfile.BadZipfile: File is not a zip file
    link_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, timeout=10)


if __name__ == '__main__':
    main()
