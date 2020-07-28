import urllib3


def download(url, user_agent=None):
    print('Downloading:', url)
    headers = {'User-agent': user_agent or 'wswp3'}
    http = urllib3.PoolManager(headers=headers)
    try:
        response = http.request('get', url)
        html = response.data
    except urllib3.exceptions.MaxRetryError as e:
        print('Download error:', e.reason)
        html = None
    if isinstance(html, bytes):
        return html.decode('utf-8')
    else:
        return html


if __name__ == '__main__':
    print(download('http://httpbin.org/headers', 'foo bar'))
