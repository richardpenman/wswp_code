import urllib3


def bytes2str(b):
    if isinstance(b, bytes):
        return b.decode('utf-8')
    else:
        return b


def download1(url):
    """Simple downloader"""
    return bytes2str(urllib3.PoolManager().request('GET', url).data)


def download2(url):
    """Download function that catches errors"""
    print('Downloading:', url)
    try:
        html = urllib3.PoolManager().request('GET', url).data
    except urllib3.exceptions.MaxRetryError as e:
        print('Download error:', e)
        html = None
    return bytes2str(html)


def download3(url, num_retries=2):
    """Download function that also retries 5XX errors"""
    print('Downloading:', url)
    try:
        response = urllib3.PoolManager().request('GET', url)
        html = response.data
        if num_retries > 0 and hasattr(response, 'status') and 500 <= response.status < 600:
            html = download3(url, num_retries - 1)
    except urllib3.exceptions.MaxRetryError as e:
        print('Download error:', e)
        html = None
    return bytes2str(html)


def download4(url, user_agent='wswp3', num_retries=2):
    """download function that includes user agent support"""
    print('downloading:', url)
    headers = {'user-agent': user_agent}
    http = urllib3.PoolManager(headers=headers)
    try:
        response = http.request('get', url)
        html = response.data
        if num_retries > 0 and hasattr(response, 'status') and 500 <= response.status < 600:
            html = download4(url, num_retries=num_retries - 1)
    except urllib3.exceptions.MaxRetryError as e:
        print('download error:', e)
        html = None
    return bytes2str(html)


def download5(url, user_agent='wswp3', proxy=None, num_retries=2):
    """download function with support for proxies"""
    print('downloading:', url)
    headers = {'user-agent': user_agent}
    if proxy is None:
        http = urllib3.PoolManager(headers=headers)
    else:
        http = urllib3.ProxyManager(proxy, headers=headers)
    try:
        response = http.request('get', url)
        html = response.data
        if num_retries > 0 and hasattr(response, 'status') and 500 <= response.status < 600:
            html = download5(url, num_retries=num_retries - 1)
    except urllib3.exceptions.MaxRetryError as e:
        print('download error:', e)
        html = None
    return bytes2str(html)


download = download5

if __name__ == '__main__':
    print(download('http://www.baidu.com'))
    print(download('http://httpstat.us/500'))
    print(download('http://httpbin.org/headers'))
    print(download('http://www.google.com', proxy='http://localhost:8118'))
    print(download('http://httpbin.org/headers', proxy='http://localhost:8118'))
    print(download('lol'))
