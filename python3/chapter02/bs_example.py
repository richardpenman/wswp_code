import urllib3
from bs4 import BeautifulSoup


def scrape(html):
    soup = BeautifulSoup(html, features='lxml')
    tr = soup.find(attrs={'id': 'places_area__row'})
    td = tr.find(attrs={'class': 'w2p_fw'})
    area = td.text
    return area


if __name__ == '__main__':
    html = urllib3.PoolManager() \
        .request('get', 'http://example.webscraping.com/places/default/view/United-Kingdom-239') \
        .data.decode('utf-8')
print(scrape(html))
