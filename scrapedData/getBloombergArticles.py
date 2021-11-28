import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

main_sitemap="https://www.bloomberg.com/feeds/businessweek/sitemap_index.xml"
main_soup=BeautifulSoup(requests.get(main_sitemap).text,'lxml')
loc_tags=main_soup.find_all('loc')


links=[]
link_count=0
for loc in loc_tags:
    if link_count>1000:
        break
    sitemap=loc.get_text()
    print(sitemap)
    sitemap_request=requests.get(sitemap,timeout=10)
    sitemap_soup=BeautifulSoup(sitemap_request.text,'lxml')
    link_tags=sitemap_soup.find_all('loc')
    for link_tag in link_tags:
        cur_link=link_tag.get_text()
        if 'news' in cur_link:
            print(cur_link)
            links.append(cur_link)
            link_count=link_count+1
            print(link_count)
            if link_count>1000:
                break