import urllib3
import lxml.html


def scrape(html):
    tree = lxml.html.fromstring(html)
    td = tree.cssselect('tr#places_area__row > td.w2p_fw')[0]
    area = td.text_content()
    return area


if __name__ == '__main__':
    html = urllib3.PoolManager() \
        .request('get', 'http://example.webscraping.com/places/default/view/United-Kingdom-239') \
        .data.decode('utf-8')
    print(scrape(html))
