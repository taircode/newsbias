import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import re


parser = argparse.ArgumentParser()
parser.add_argument("--category", "-c", default="top")
args = parser.parse_args()

if args.category == "top":
    rss_url="https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best"
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

#the page denies GET requests that don't identify a User-Agent
headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36'}

html_request = requests.get(rss_url, headers=headers)

article_list_soup=BeautifulSoup(html_request.text,"lxml")
all_as=article_list_soup.find_all("a", href=lambda href: href and "app" in href)

#probably a faster way than looping to do this that's built in to beautiful soup
links=[]
for item in all_as:
    links.append(item.get("href"))
print(len(links))

titles=[]
articles=[]

count=0
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
    #how do we want to join these paragraph? 
    article = '\n'.join(bodytext)
    print(article)

    articles.append(article)
    count=count+1

print(f"count={count}")

labels=[3]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("Reutersdata.csv")

#if appending, change mode to "a" and specify header=False
#atafile = df.to_csv("CNNdata.csv",mode="a", header=False)