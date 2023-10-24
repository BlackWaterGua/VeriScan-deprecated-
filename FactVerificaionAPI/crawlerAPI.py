import requests
import re
from bs4 import BeautifulSoup

# craw html from url and return web text with a string
# the result text is divided with ",", without handling more punctuations like "，", "。", "[]"
def url_to_text(url):
    # the API only use these parameters
    JSON = {
        "urls": url,
        "cache": False,
        "timeout": 15000
    }
    # use API
    web = requests.post("http://140.115.54.45:6789/post/crawler/static/html", json=JSON)
    # filter the content of return string
    soup = BeautifulSoup(web.content, 'html.parser')
    text = soup.get_text().replace(' ','')
    dr = re.compile(r'(\\t)+(\\n)*|(\\t)*(\\n)+')
    text = dr.sub(',',text)
    dr = re.compile(',+')
    text = dr.sub(',',text)

    return text