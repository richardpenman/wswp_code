import zlib
try:
    import cPickle as pickle
except ImportError:
    import pickle
from datetime import datetime, timedelta
from pymongo import MongoClient, errors
from bson.binary import Binary

"""
indexes?
compare performance with HBase
"""


class MongoCache:
    """
    Wrapper around MongoDB to cache downloads

    >>> client = MongoClient('localhost', 27017)
    >>> cache = MongoCache(client)
    >>> cache.clear()
    >>> url = 'http://example.com/abc'
    >>> result = {'html': '<html>abc</html>'}
    >>> cache[url] = result
    >>> cache[url]['html'] == result['html']
    True
    >>> cache = MongoCache(client, timedelta(days=0))
    >>> cache[url] = result
    >>> cache[url] 
    Traceback (most recent call last):
    ...
    KeyError: 'http://example.com/abc has expired'
    """
    def __init__(self, client, expires=timedelta(days=30)):
        """
        client: mongo database client
        expires: timedelta of amount of time before a cache entry is considered expired
        """
        self.client = client
        self.expires = expires

    def __contains__(self, url):
        try:
            self[url]
        except KeyError:
            return False
        else:
            return True
    
    def __getitem__(self, url):
        """Load value at this URL
        """
        record = self.client.cache.webpage.find_one({'_id': url})
        if record:
            if self.has_expired(record['timestamp']):
                raise KeyError(url + ' has expired')
            else:
                return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + ' does not exist')


    def __setitem__(self, url, result):
        """Save value for this URL
        """
        record = {'result': Binary(zlib.compress(pickle.dumps(result))), 'timestamp': datetime.now()}
        self.client.cache.webpage.update({'_id': url}, {'$set': record}, upsert=True)


    def __delitem__(self, url):
        """Remove the value at this key and any empty parent sub-directories
        """
        self.client.cache.webpage.remove(url=url)

    
    def has_expired(self, timestamp):
        """Return whether this timestamp has expired
        """
        return datetime.now() > timestamp + self.expires


    def clear(self):
        self.client.cache.webpage.drop()
