import requests
from bs4 import BeautifulSoup
import pandas as pd

#there are articles from October
sitemap="https://www.cnn.com/article/sitemap-2021-10.html"

sitemap_request=requests.get(sitemap)
sitemap_soup=BeautifulSoup(sitemap_request.text,'lxml')

all_spans=sitemap_soup.find_all("span", {'class': 'sitemap-link'})
print(len(all_spans))

links=[]

for span in all_spans:
    a=span.find("a")
    if a is not None:
        link=a.get("href")
        links.append(link)
        
titles=[]
articles=[]
count=0

for current_link in links:
    #print(current_link)
    if current_link.startswith('https://www.cnn.com/20'):
        r=requests.get(current_link,timeout=10)
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
            #print(fullbody)
            count=count+1
            if count % 100 ==0:
                print(current_link)
                print(count)
    else:
        print("Bad link, ignoring it:")

print(f"count={count}")

labels=[2]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("raw_articles/CNNData.csv")

#if appending, change mode to "a" and specify header=False
#atafile = df.to_csv("CNNdata.csv",mode="a", header=False)
