import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import re
import json

frontpage="https://www.cnn.com/"
main_list="https://www.cnn.com/services/rss/"
international_list="http://edition.cnn.com/services/rss/"
money_list="https://money.cnn.com/services/rss/"

"""If you want to get frontpage articles
frontpage_request=requests.get(frontpage)
frontpage_soup=BeautifulSoup(frontpage_request.text,"lxml")

script=frontpage_soup.find("script", text=re.compile(r'articleList'))

print(script)

pattern = re.compile('"uri":"(/2021/.*?)"')
uris=re.findall(pattern,script.text)
print(uris)
print(len(uris))
links=[]
for uri in uris:
    links.append("https://www.cnn.com/"+uri)
"""

main_links=[main_list,international_list]

#do we want the titles?
titles=[]
articles=[]
count=0

for item in main_links:
    main_request = requests.get(item)
    main_soup = BeautifulSoup(main_request.text,"lxml")
    all_rss_feeds=main_soup.find_all("link", {'rel': re.compile(r'alternate')})

    topic_links=[]
    for item in all_rss_feeds:
        current_link=item.get("href")
        print(current_link)
        topic_links.append(current_link)
    print(len(topic_links))

    for rss_url in topic_links:
        print(f"Current RSS feed: {rss_url}\n")
        html_request = requests.get(rss_url)
        #print(type(html_request))

        #this is a soup object that is the list of articles
        article_list_soup=BeautifulSoup(html_request.text,"lxml")

        all_guid=article_list_soup.find_all("guid")

        print(len(all_guid))

        for guid in all_guid:
            current_link=guid.get_text()
            if current_link.startswith('https://www.cnn.com/20'):
                print(current_link)
                r=requests.get(current_link)
                html_source=r.text

                #various options for parsers: "html.parser"
                soup=BeautifulSoup(html_source,"lxml")

                #print("\n")
                #print("\n")
                #print("Next Article: ")
                #print(soup.find("title"))
                #print("\n")

                titles.append(soup.find("title").get_text())
                
                #The first line of the article is always different for some reason, probably cause of different style formating of the first line
                first_line=soup.find_all("p",class_="zn-body__paragraph speakable")
                body_pars=soup.find_all("div", class_="zn-body__paragraph")
                fullbody=""
                for div in first_line:
                    fullbody=fullbody+div.get_text()
                #print("\n")
                for div in body_pars:
                    fullbody=fullbody+div.get_text()
                #print(fullbody)
                if fullbody=="":
                    print("this article is empty!")
                else:
                    articles.append(fullbody)
                    count=count+1
            else:
                print("Bad link, ignoring it:")
                print(current_link)

print(f"count={count}")

labels=[2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("scrapedData/CNNdata.csv")

#if appending, change mode to "a" and specify header=False
#atafile = df.to_csv("CNNdata.csv",mode="a", header=False)