import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

#The main sitemap is https://www.msnbc.com/archive/articles
#Use this for all of the years and months

#If you want more data, use the other months
sitemaps=["https://www.msnbc.com/archive/articles/2021/september","https://www.msnbc.com/archive/articles/2021/october"]
sitemap_soups=[]
for map in sitemaps:
    sitemap_request=requests.get(map)
    sitemap_soups.append(BeautifulSoup(sitemap_request.text,'lxml'))

links=[]

for sitemap_soup in sitemap_soups:
    main=sitemap_soup.find('main')
    a_tags=main.find_all('a')
    for a_tag in a_tags:
        links.append(a_tag.get('href'))

print(f"Found {len(links)} many links.")

titles=[]
articles=[]
count=0

for link in links:
    if 'transcript' not in link:
        print(link)
        r=requests.get(link,timeout=10)
        html_source=r.text

        #various options for parsers: "html.parser"
        soup=BeautifulSoup(html_source,"lxml")

        div=soup.find("div",{'class': 'article-body__content article-body-font--loading'})
        article_body=div.get_text()
        #print(article_body)
        articles.append(article_body)
        count=count+1
        print(count)

print(f"count={count}")

labels=[2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("scrapedData/MSNBCdata.csv")