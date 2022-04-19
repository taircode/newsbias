import torch
import pandas as pd
import numpy as np
from datasets import load_dataset

"""
Assuming articles already scraped and labelled in /scrapedData/raw_articles/[journal_name].csv
Combine all articles into list, randomize, and divide into train.csv and eval.csv
Save train.csv and eval.csv to /articles/
"""

#first merge all of the CSVs

#you should probably make a list or dictionary containing labels
#these are the most factual - label=0
reuters=pd.read_csv("../scrapedData/raw_articles/Reutersdata.csv", usecols=['article','label'])

#these are second most factual - label=1
economist=pd.read_csv("../scrapedData/raw_articles/EconomistData.csv", usecols=['article','label'])
newyorker=pd.read_csv("../scrapedData/raw_articles/NewYorkerData.csv", usecols=['article','label'])
nationalreview=pd.read_csv("../scrapedData/raw_articles/NationalReviewData.csv", usecols=['article','label'])

#these are third most factual - label=2
cnn=pd.read_csv("../scrapedData/raw_articles/CNNData.csv", usecols=['article','label'])
msnbc=pd.read_csv("../scrapedData/raw_articles/MSNBCData.csv", usecols=['article','label'])

#these are forth most factual - label=3
dailymail=pd.read_csv("../scrapedData/raw_articles/DailyMailData.csv", usecols=['article','label'])
fox=pd.read_csv("../scrapedData/raw_articles/FoxNewsData.csv", usecols=['article','label'])

frames_dict={
    "reuters": reuters,
    "economist": economist,
    "newyorker": newyorker,
    "nationalreview": nationalreview,
    "cnn": cnn,
    "msnbc": msnbc,
    "dailymail": dailymail,
    "fox": fox,
}

for item in frames_dict.items():
    print(f"{item[0]} has length {len(item[1]['article'])}")

#reuters=reuters.rename(columns={'label': 'labels'})
#economist=economist.rename(columns={'label': 'labels'})
#cnn=cnn.rename(columns={'label': 'labels'})
#dailymail=dailymail.rename(columns={'label': 'labels'})

#making sure that there are no empty strings, i.e. NaNs. DailyMail was letting some slip through.
for key in frames_dict:
    nulls=np.where(pd.isnull(frames_dict[key]['article']))
    frames_dict[key]=frames_dict[key].drop(nulls[0])

#get rid of the city, country '(Reuters) - ' beginnings
for idx in range(len(frames_dict['reuters'])):
    current = frames_dict['reuters'].loc[idx,'article']
    index=current.find('(Reuters) - ')
    if index != -1:
        frames_dict['reuters'].loc[idx,'article']=current[index+len('(Reuters) - '):]
    else:
        index=current.find('( Reuters Breakingviews )')
        if index != -1:
            frames_dict['reuters'].loc[idx,'article']=current[index+len('( Reuters Breakingviews )'):]

#get rid of the city, country '(CNN)' beginnings
for idx in range(len(frames_dict['cnn'])):
    current = frames_dict['cnn'].loc[idx,'article']
    index=current.find('(CNN)')
    if index != -1:
        frames_dict['cnn'].loc[idx,'article']=current[index+len('(CNN)'):]
    else:
        index=current.find('(CNN Business)')
        if index != -1:
            frames_dict['cnn'].loc[idx,'article']=current[index+len('(CNN Business)'):]

#The economist and dailymail don't have these beginnings

#this should have already been done when collecting the articles - maybe the labelling should be done here
frames_dict['reuters'] = frames_dict['reuters'].assign(label=0)

frames_dict['economist'] = frames_dict['economist'].assign(label=1)
frames_dict['newyorker'] = frames_dict['newyorker'].assign(label=1)
frames_dict['nationalreview'] = frames_dict['nationalreview'].assign(label=1)

frames_dict['cnn'] = frames_dict['cnn'].assign(label=2)
frames_dict['msnbc'] = frames_dict['msnbc'].assign(label=2)

frames_dict['dailymail'] = frames_dict['dailymail'].assign(label=3)
frames_dict['fox'] = frames_dict['fox'].assign(label=3)

full_dataset=pd.concat(list(frames_dict.values()), ignore_index=True)

print(full_dataset)

#reset_index creates a new column of indices from 0 to len in order, i.e. not shuffled, and drop=True prevents a column of old shuffled indices
permuted_dataset=full_dataset.sample(frac=1).reset_index(drop=True)

#print(permuted_dataset)

train, val = np.split(permuted_dataset,[int(.8*len(permuted_dataset))])
print(f"Full dataset size is {len(permuted_dataset)}")
print(f"Train dataset size is {len(train)}")
print(f"Eval dataset size is {len(val)}")

train.to_csv("../articles/train.csv")
val.to_csv("../articles/eval.csv")