import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import re
import json

main_url="https://www.dailymail.co.uk/home/article-2684527/RSS-Feeds.html"

#main url is above, but let's just use a couple of rss feeds for now

link1="https://www.dailymail.co.uk/news/index.rss"
link2="https://www.dailymail.co.uk/ushome/index.rss"

topic_links=[link1, link2]

articles=[]
titles=[]
count=0

for topic_url in topic_links:

    print(f"CURRENT RSS FEED LINK IS {topic_url}")
    html_request=requests.get(topic_url)
    #note that this didn't work for Economist when I used lxml, it's an xml as you can see above
    article_list_soup = BeautifulSoup(html_request.text,"xml")

    #print(article_list_soup)

    all_links=article_list_soup.find_all("link")
    #first two links are just to the home page and third one is empty for some reason
    all_links=all_links[3:]
    
    for current_link in all_links:
        print("Here is the current link")
        print(current_link.text+"\n")
        if "cartoon" in current_link.text or "sources" in current_link.text:
            print("Cartoon Link or Sources Link, so exciting\n")
        else:
            r=requests.get(current_link.text,timeout=10)
            print(f"Request statis is {r.status_code}")
            html_source=r.text

            #various options for parsers: "html.parser"
            soup=BeautifulSoup(html_source,"lxml")

            #print(soup)


            #type="application/ld+json"
            div = soup.find("div", itemprop="articleBody")
            all_ps=div.find_all(lambda tag: tag.name == 'p' and 'imageCaption' not in tag['class'])

            bodytext=[e.get_text() for e in all_ps]

            if len(bodytext)==0:
                print("EMPTY ARTICLE")
            else:
                #how do we want to join these paragraph? 
                article = '\n'.join(bodytext)
                print(article+"\n")

                articles.append(article)
                count=count+1

labels=[-2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("DailyMaildata.csv")

#implement append version down here if you want - see geteconomistarticles