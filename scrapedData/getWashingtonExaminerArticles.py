

# this is the main sitemap with years, months, days https://www.washingtonexaminer.com/sitemap

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

#The main sitemap is https://www.msnbc.com/archive/articles
#Use this for all of the years and months

#If you want more data, use the other months
october_days=[]
october_soups=[]
for i in range(30):
    date=i+1
    #october_days.append("https://www.washingtonexaminer.com/sitemap/2021/10/"+str(date))
    print("https://www.washingtonexaminer.com/sitemap/2021/10/"+str(date))
    day_request=requests.get("https://www.washingtonexaminer.com/sitemap/2021/10/"+str(date))
    print(day_request)
    october_soups.append(BeautifulSoup(day_request.text,'lxml'))
    print(october_soups[i].prettify())

links=[]

for day_soup in october_soups:
    main_div=day_soup.find('div',{'class':'ArchivePage-items col-12 mb-4'})
    a_tags=main_div.find_all('a', {'class': "Link"})
    for a_tag in a_tags:
        links.append(a_tag.get('href'))

print(f"Found {len(links)} many links.")
exit()

#haven't implemented below this yet

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

        div=soup.find("div",{'class': 'article-body__content article-body-font--loading'})
        article_body=div.get_text()
        #print(article_body)
        articles.append(article_body)
        count=count+1
        print(count)

print(f"count={count}")

labels=[2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("MSNBCdata.csv")