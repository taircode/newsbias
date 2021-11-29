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
    if link_count>10:
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
            if link_count>10:
                break


#<div class="body-copy-v2"


print(f"Found {len(links)} many links.")
titles=[]
articles=[]
count=0

for link in links:
    print(link)
    r=requests.get(link,timeout=10)
    html_source=r.text
    print(html_source)
    #various options for parsers: "html.parser"
    #class="body-copy fence-body"
    soup=BeautifulSoup(html_source,"lxml")
    p_tags=soup.find_all("div",{'class': "body-copy fence-body"})
    for p in p_tags:
        print(p.prettify())
    exit()
    if div is not None:
        article_body=div.get_text()
        print(article_body)
        #print(article_body)
        articles.append(article_body)
        count=count+1
        if count%100==0:
            print(count)

print(f"count={count}")

labels=[0]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("raw_articles/BloombergData.csv")