import urllib2
import urllib

from BeautifulSoup import BeautifulSoup

def fetch(page, fetch_lib=urllib2):
    req = fetch_lib.Request(
        'http://en.wikipedia.org/wiki/%s' % urllib.quote(page)
    )
    try:
        req.add_header('User-agent', 'Mozilla/5.0')
        result = fetch_lib.urlopen(req)
        content = result.read()
        
        soup = BeautifulSoup(content)
        div = soup.find(id='bodyContent')
        par = div.find('p', recursive=False)
        return unicode(par)
    except:
        return u''
