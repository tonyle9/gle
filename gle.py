import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from urllib.parse import parse_qs

class Google:
    URL_HOME   = 'https://www.google.com'
    URL_SEARCH = 'https://www.google.com/search?%s'

    def __init__(self, count=3, params={'tld':'com', 'hl':'en', 
        'tbs':'0', 'safe':'off', 'tpe':''}):
        assert count >= 1, 'Invalid page count!'
        self.count  = count
        self.params = params

        req = requests.get(self.URL_HOME)
        self.cookies = req.cookies

    def search(self, data):
        self.params['q'] = data
        url = self.URL_SEARCH % urlencode(self.params)
        req = requests.get(url, cookies=self.cookies)
        next, hits = self.build(req.text)
        yield hits

        for ind in range(self.count - 1):
            next, hits = self.build(requests.get(
                    next, cookies=self.cookies).text)
            yield hits
            if not next: break

    def build(self, html):
        dom  = BeautifulSoup(html, 'lxml')
        next = dom.find('a', {'class':'fl'}).get('href')
        next = '%s%s' % (self.URL_HOME, next)
        return next, self.get_hits(dom)

    def get_hits(self, dom):
        elems = dom.find_all('div', {'class':'g'})

        for indi in elems:
            for indj in self.ext_hit(indi):
                yield indj

    def ext_hit(self, hit):
        title = hit.find('h3', {'class': 'r'})
        desc  = hit.find('span', {'class': 'st'})
        url   = hit.find('a')

        if title and desc and url:
            yield {'title':  title.text, 'desc': desc.text, 
                'url': parse_qs(url.get('href'))['/url?q'][0], }


