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

""" Here are the links
0<li><a href="/the-world-this-week/rss.xml">The world this week</a></li>
<li><a href="/letters/rss.xml">Letters</a></li> DON'T WANT THIS ONE
1<li><a href="/leaders/rss.xml">Leaders</a></li>
2<li><a href="/briefing/rss.xml">Briefings</a></li>
3<li><a href="/special-report/rss.xml">Special reports</a></li>
4<li><a href="/britain/rss.xml">Britain</a></li>
5<li><a href="/europe/rss.xml">Europe</a></li>
6<li><a href="/united-states/rss.xml">United States</a></li>
7<li><a href="/the-americas/rss.xml">The Americas</a></li>
8<li><a href="/middle-east-and-africa/rss.xml">Middle East and Africa</a></li>
9<li><a href="/asia/rss.xml">Asia</a></li>
10<li><a href="/china/rss.xml">China</a></li>
11<li><a href="/international/rss.xml">International</a></li>
12<li><a href="/business/rss.xml">Business</a></li>
13<li><a href="/finance-and-economics/rss.xml">Finance and economics</a></li>
14<li><a href="/science-and-technology/rss.xml">Science and technology</a></li>
<li><a href="/books-and-arts/rss.xml">Books and arts</a></li> DON'T WANT THIS ONE
<li><a href="/obituary/rss.xml">Obituaries</a></li> DON'T WANT THIS ONE
<li><a href="/graphic-detail/rss.xml">Graphic detail</a></li> DON'T WANT THIS ONE
<li><a href="/economic-and-financial-indicators/rss.xml">Indicators</a></li> DON'T WANT THIS ONE
"""

topic_links=[]
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

#if you want a smaller batch
#topic_links=topic_links[10:15]

#topic_url=topic_links[4]
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
            r=requests.get(current_link.text,timeout=10)
            print(f"Request statis is {r.status_code}")
            html_source=r.text

            #various options for parsers: "html.parser" #wait shouldn't this be lxml?
            soup=BeautifulSoup(html_source,"xml")

            #print(soup)


            #type="application/ld+json"
            script = soup.find("script", text=re.compile(r'articleBody'))
            #print(script)
            if script is not None:
                data = json.loads(script.text)
                bodytext=data['articleBody']
                title=data['headline']
                if len(bodytext) ==0:
                        print("EMPTY ARTICLE")
                else:
                    #print("Adding the current article:\n")
                    #print(bodytext+"\n")
                    titles.append(title)
                    articles.append(bodytext)
                    count=count+1

print(count)
print(len(articles))

labels=[2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

old_df=pd.read_csv("EconomistData.csv", usecols=['article','label'])
df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
new_df=pd.concat([old_df,df],ignore_index=True)

datafile = new_df.to_csv("EconomistData.csv")