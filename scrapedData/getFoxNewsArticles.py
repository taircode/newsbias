

#main sitemap is https://www.foxnews.com/sitemap.xml
#lower links are more recent

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json

#The main sitemap is https://www.msnbc.com/archive/articles
#Use this for all of the years and months

#If you want more data, use more links from the above sitemap - note a single one of these has about 5k articles
sitemaps=["https://www.foxnews.com/sitemap.xml?type=articles&from=1635554419000"]
sitemap_soups=[]
for map in sitemaps:
    sitemap_request=requests.get(map)
    sitemap_soups.append(BeautifulSoup(sitemap_request.text,'lxml'))

print(len(sitemap_soups))

links=[]

for sitemap_soup in sitemap_soups:
    loc_tags=sitemap_soup.find_all('loc')
    for loc in loc_tags:
        links.append(loc.get_text())
        if len(links)>2000:
            break

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

        #pattern=re.compile('props:{text:')
        #script=soup.find('script',text=pattern)
        #print(script.text)
        #match = pattern.search(script.text)
        #print(match)

        #if script is not None:
            #s1.find(s2)
            #print(script.text.find('{return'))
            #idx=script.text.find('{return')
            #print(script.text[idx:])
            #mylist=list(script.text[idx:])
            #mylist = script.text[idx:].split(",")
            #for item in mylist:
            #    print(item)
            #data = json.loads(script.text[idx:])
            #print(data)

        div=soup.find('div',{'class':'article-body'})
        #print(div.get_text())
        #print(div.prettify())
        p_tags=div.find_all('p')
        bodytext=[]
        for tag in p_tags:
            text=tag.get_text()
            if 'Photo' not in text and 'click' not in text and 'CLICK' not in text and 'via' not in text:
                bodytext.append(tag.get_text())
        #print(div.parent)
        #exit()
        
        article_body= ''.join(bodytext)
        #print(article_body)
        articles.append(article_body)
        count=count+1
        if count%100==0:
            print(count)

print(f"count={count}")

labels=[2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("raw_articles/FoxNewsData.csv")