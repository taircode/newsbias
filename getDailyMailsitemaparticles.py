import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

sitemap="https://www.dailymail.co.uk/sitemap-articles-year~2021.xml"

sitemap_request=requests.get(sitemap)
sitemap_soup=BeautifulSoup(sitemap_request.text,'lxml')

#links=sitemap_soup.find_all(lambda tag: tag.name == 'loc')
#links=sitemap_soup.find_all(re.compile(r'loc'))

feeds=sitemap_soup.find_all('loc')
print(f"There are {len(feeds)} feeds in the master sitemap xml")

links=[]
for feed in feeds:
    if len(links)<3500:
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

for current_link in links:
    #print(current_link.text)
    if "cartoon" in current_link or "sources" in current_link:
        print("Cartoon Link or Sources Link, so exciting\n")
    else:
        r=requests.get(current_link,timeout=10)
        #print(f"Request statis is {r.status_code}")
        html_source=r.text

        #various options for parsers: "html.parser"
        soup=BeautifulSoup(html_source,"lxml")

        #print(soup)
        title=soup.find("title").text
        titles.append(title)

        #type="application/ld+json"
        div = soup.find("div", itemprop="articleBody")
        #print(div)
        #print("HERE ARE THE ATTRIBUTES OF THE FIRST P")
        #print(div.find("p").attrs)
        #this is why find_all is probably better, so you get an empty list rather than a single None-type
        if div is not None:
            all_ps=div.find_all("p", {"class": "mol-para-with-font"})

            """Here's the one line code I had before. The issue is that you might get a p tag that doesn't have a class attribute at all"""
            """There's probably a way to deal with this in the single line"""
            #body_paragraphs=div.find_all(lambda tag: tag.name == 'p' and 'imageCaption' not in tag['class'])

            #body_paragraphs=[]
            #for item in all_ps:
            #    if 'class' in item.attrs:
            #        if 'imageCaption' not in item['class']:
            #            body_paragraphs.append(item)
            #    else:
            #        print(f"Here are the attributes of a p without class {item.attrs}")

            bodytext=[e.get_text() for e in all_ps]

            if len(bodytext)==0:
                print("EMPTY ARTICLE")
            else:
                #how do we want to join these paragraph? 
                article = '\n'.join(bodytext)
                articles.append(article)
                count=count+1
                if count%100==0:
                    print(count)
                    print(f"Article title: {title}")
                    print(current_link)
                    print(article)

labels=[3]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("scrapedData/DailyMaildata.csv")

#implement append version down here if you want - see geteconomistarticles