import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

#The main sitemap is https://www.nationalreview.com/sitemap.xml
#Use this for all of the years and months


main_sitemap="https://www.nationalreview.com/sitemap.xml"
main_soup=BeautifulSoup(requests.get(main_sitemap).text,'lxml')
loc_tags=main_soup.find_all('loc')


links=[]
link_count=0
for loc in loc_tags:
    if link_count>1000:
        break
    sitemap=loc.get_text()
    print(sitemap)
    sitemap_request=requests.get(sitemap,timeout=10)
    sitemap_soup=BeautifulSoup(sitemap_request.text,'lxml')
    link_tags=sitemap_soup.find_all('loc')
    for link_tag in link_tags:
        cur_link=link_tag.get_text()
        if 'news' in cur_link:
            print(cur_link)
            links.append(cur_link)
            link_count=link_count+1
            print(link_count)
            if link_count>1000:
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
    partial=soup.find("div",{'id':"article-content-truncate-wrap"})
    if partial:
        print("This article isn't loading")
    else:
        div=soup.find('div',{'class':"article-content"})
        if div is not None:
            p_tags=div.find_all('p')
            bodytext=[]
            for tag in p_tags:
                text=tag.get_text()
                if 'Send' not in text:
                    bodytext.append(tag.get_text())                
            article_body= ''.join(bodytext)
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
datafile = df.to_csv("raw_articles/NationalReviewdata.csv")