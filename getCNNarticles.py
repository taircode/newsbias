import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--category", "-c", default="top")
args = parser.parse_args()

if args.category == "top":
    rss_url="http://rss.cnn.com/rss/cnn_topstories.rss"
elif args.category == "world":
    rss_url="http://rss.cnn.com/rss/cnn_world.rss"
elif args.category == "us":
    rss_url="http://rss.cnn.com/rss/cnn_us.rss"
#elif args.category == "business":
#    rss_url="http://rss.cnn.com/rss/money_latest.rss"
elif args.category == "sports":
    rss_url="http://rss.cnn.com/rss/edition_sport.rss"
elif args.category == "politics":
    rss_url="http://rss.cnn.com/rss/cnn_allpolitics.rss"
elif args.category == "tech":
    rss_url="http://rss.cnn.com/rss/cnn_tech.rss"
elif args.category == "health":
    rss_url="http://rss.cnn.com/rss/cnn_health.rss"
elif args.category == "entertainment":
    rss_url="http://rss.cnn.com/rss/cnn_showbiz.rss"
#elif args.category == "travel":
#    rss_url="http://rss.cnn.com/rss/cnn_travel.rss"

html_request = requests.get(rss_url)
#print(type(html_request))

with open('tech_rss.html','w') as f:
    f.write(html_request.text)

with open('tech_rss.html','r') as f:
    soup=BeautifulSoup(f,"lxml")

all_guid=soup.find_all("guid")

print(len(all_guid))

#do we want the titles?
titles=[]
articles=[]

count=0
for guid in all_guid:
    current_link=guid.get_text()
    if current_link.startswith('https://www.cnn.com/20'):
        print(current_link)
        filename=current_link+".html"
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

labels=[0]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("CNNdata.csv",mode="a")

#if appending, change mode to "a" and specify header=False
#atafile = df.to_csv("CNNdata.csv",mode="a", header=False)