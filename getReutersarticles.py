import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import re

#This url contains link so to rss feeds by topic
main_url="https://www.reutersagency.com/en/reutersbest/reuters-best-rss-feeds/#recent-content"

#the page denies GET requests that don't identify a User-Agent
headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36'}

main_html = requests.get(main_url, headers=headers)
main_html_soup = BeautifulSoup(main_html.text,"lxml")
all_rss_feeds=main_html_soup.find_all("a",href=lambda href: href and "/feed/" in href)
topic_links=[]
for item in all_rss_feeds:
    current_link=item.get("href")
    print(current_link)
    topic_links.append(current_link)
print(len(topic_links))

titles=[]
articles=[]
count=0

for rss_url_ending in topic_links:
    rss_url="https://www.reutersagency.com"+rss_url_ending

    html_request = requests.get(rss_url, headers=headers)

    article_list_soup=BeautifulSoup(html_request.text,"lxml")
    all_as=article_list_soup.find_all("a", href=lambda href: href and "app" in href)

    #probably a faster way than looping to do this that's built in to beautiful soup
    links=[]
    for item in all_as:
        links.append(item.get("href"))
    print(len(links))

    for link in links:
        print(link+"\n")
        r=requests.get(link)
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
        print(f"Title:{title}\n")
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
            print(article+"\n")

            articles.append(article)
            count=count+1

print(f"count={count}")

labels=[3]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("scrapedData/Reutersdata.csv")

#if appending, change mode to "a" and specify header=False
#atafile = df.to_csv("CNNdata.csv",mode="a", header=False)