import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import re
import json

titles=[]
articles=[]
count=0

main_url = "https://www.economist.com/rss"
main_request = requests.get(main_url)
main_soup=BeautifulSoup(main_request.text,"lxml")
#we want link-right because these are the print edition, the links-left are blogs, we don't want that
links_div=main_soup.find("div", {'class':'ec-rss-links-right grid-3'})
all_rss_feeds=links_div.find_all("a")

topic_links=[]
topic_links.append("https://www.economist.com/the-world-this-week/rss.xml")
topic_links.append("https://www.economist.com/the-world-this-week/rss.xml")
for item in all_rss_feeds:
    current_ending=item.get("href")
    if "letters" in current_ending or "books" in current_ending or "obituary" in current_ending or "graphic" in current_ending or "economic" in current_ending:
        print(f"DON'T WANT {current_ending}")
    else:
        topic_links.append("https://www.economist.com"+current_ending)

#got all of the rss topic links
titles=[]
articles=[]
count=0

for topic_url in topic_links:
    print(f"CURRENT RSS FEED LINK IS {topic_url}")
    html_request=requests.get(topic_url)
    #note that this didn't work for Economist when I used lxml, it's an xml as you can see above
    article_list_soup = BeautifulSoup(html_request.text,"xml")

    #print(article_list_soup)

    all_links=article_list_soup.find_all("link")
    #first link is to the rss page you're already 
    all_links=all_links[1:]

    print(f"This RSS feed has {len(all_links)} links\n")

    for current_link in all_links:
        print("Here is the current link")
        print(current_link.text+"\n")
        if "cartoon" in current_link.text or "sources" in current_link.text:
            print("Cartoon Link or Sources Link, so exciting\n")
        else:
            r=requests.get(current_link.text)
            html_source=r.text

            #various options for parsers: "html.parser"
            soup=BeautifulSoup(html_source,"xml")

            #print(soup)

            #get title
            #title=soup.find("title").get_text()
            #print(f"Title:{title}\n")
            #titles.append(title)

            #type="application/ld+json"
            script = soup.find("script", text=re.compile(r'articleBody'))
            #print(script)
            if script is not None:
                data = json.loads(script.text)
                bodytext=data['articleBody']
                if len(bodytext) ==0:
                        print("EMPTY ARTICLE")
                else:
                    print("Adding the current article:\n")
                    print(bodytext+"\n")
                    articles.append(bodytext)
                    count=count+1

print(count)
print(len(articles))

labels=[2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("EconomistData.csv")