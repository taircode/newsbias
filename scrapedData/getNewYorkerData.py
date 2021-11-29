import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

#The main sitemap is https://www.newyorker.com/sitemap
#Use this for all of the years and months


main_sitemap="https://www.newyorker.com/sitemap"
main_soup=BeautifulSoup(requests.get(main_sitemap).text,'lxml')
main_div=main_soup.find('div',{'class':'SitemapArchive__sitemap___3t764'})
a_tags=main_div.find_all('a')

links=[]
link_count=0
for a in a_tags:
    if link_count>900:
        break
    map=a.get_text()
    #print(map)
    sitemap_request=requests.get(map,timeout=10)
    sitemap_soup=BeautifulSoup(sitemap_request.text,'lxml')
    main=sitemap_soup.find('div',{'class':'SitemapArchive__sitemap___3t764'})
    a_tags=main.find_all('a')
    for a_tag in a_tags:
        cur_link=a_tag.get('href')
        if 'news' in cur_link:
            print(cur_link)
            links.append(cur_link)
            link_count=link_count+1
            #print(link_count)
            if link_count%100==0:
                print(link_count)
            if link_count>900:
                break

#<div class="SitemapArchive__sitemap___3t764">
#<section class="PageContainer__pageContent___1xERg undefined">

print(f"Found {len(links)} many links.")
titles=[]
articles=[]
count=0

for link in links:
    print(link)
    r=requests.get(link,timeout=10)
    html_source=r.text

    #various options for parsers: "html.parser"
    soup=BeautifulSoup(html_source,"lxml")

    div=soup.find("div",{'class': 'body__inner-container'})
    if div is not None:
        article_body=div.get_text()
        #print(article_body)
        articles.append(article_body)
        count=count+1
        if count%100==0:
            print(count)

print(f"count={count}")

labels=[1]*count
print(labels)

#this should have a list of lists that is [article, label] pairs
list_of_datapairs = list(zip(articles, labels))

df = pd.DataFrame(list_of_datapairs, columns=["article","label"])
datafile = df.to_csv("raw_articles/NewYorkerData.csv")