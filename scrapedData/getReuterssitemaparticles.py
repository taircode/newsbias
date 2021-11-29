import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


"""This is another sitemap, how is it different?"""
#other_sitemap="https://www.reuters.com/arc/outboundfeeds/sitemap/?outputType=xml"

sitemap="https://www.reuters.com/arc/outboundfeeds/news-sitemap-index/?outputType=xml"
sitemap_request=requests.get(sitemap)
sitemap_soup=BeautifulSoup(sitemap_request.text,'lxml')

#links=sitemap_soup.find_all(lambda tag: tag.name == 'loc')
#links=sitemap_soup.find_all(re.compile(r'loc'))

feeds=sitemap_soup.find_all('loc')
print(len(feeds))

links=[]
for feed in feeds:
    print(feed.text)
    feed_request=requests.get(feed.text)
    feed_soup=BeautifulSoup(feed_request.text,'lxml')

    locs=feed_soup.find_all('loc')
    print(len(locs))
    for loc in locs:
        #print(loc.text)
        links.append(loc.text)

titles=[]
articles=[]
count=0

for link in links:
    r=requests.get(link,timeout=10)
    html_source=r.text

    #various options for parsers: "html.parser"
    soup=BeautifulSoup(html_source,"lxml")

    #print("\n")
    #print("\n")
    #print("Next Article: ")
    #print(soup.find("title"))
    #print("\n")

    #print(bodytext)

    #get title
    title=soup.find("title").get_text()
    titles.append(title)

    #get article body
    #was trying to use lambda notation, but ended up just using regular expression
    #bodytext=[e.get_text() for e in soup.find_all(lambda tag:tag.name=="p" and "paragraph" in tag.data-testid)]
    bodytext=[e.get_text() for e in soup.find_all("p", {'data-testid': re.compile(r'paragraph')})]

    if len(bodytext) ==0:
        print("EMPTY ARTICLE")
    else:
        #how do we want to join these paragraph? 
        article = '\n'.join(bodytext)
        #print(article+"\n")
        articles.append(article)
        count=count+1
        if count%25==0:
            print(count)
            print(f"Title:{title}")
            print(link+"\n")

print(f"count={count}")

labels=[0]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("raw_articles/ReutersData.csv")

#if appending, change mode to "a" and specify header=False
#atafile = df.to_csv("CNNdata.csv",mode="a", header=False)