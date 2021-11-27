import torch
import pandas as pd
import numpy as np
from datasets import load_dataset

#first merge all of the CSVs

reuters=pd.read_csv("../scrapedData/Reutersdata.csv", usecols=['article','label'])
economist=pd.read_csv("../scrapedData/EconomistData.csv", usecols=['article','label'])
cnn=pd.read_csv("../scrapedData/CNNdata.csv", usecols=['article','label'])
dailymail=pd.read_csv("../scrapedData/DailyMaildata.csv", usecols=['article','label'])

#reuters=reuters.rename(columns={'label': 'labels'})
#economist=economist.rename(columns={'label': 'labels'})
#cnn=cnn.rename(columns={'label': 'labels'})
#dailymail=dailymail.rename(columns={'label': 'labels'})

#making sure that there are no empty strings, i.e. NaNs, DailyMail was letting some slip through
nulls=np.where(pd.isnull(dailymail['article']))
dailymail=dailymail.drop(nulls[0])
#print(len(nulls[0]))

nulls=np.where(pd.isnull(economist['article']))
economis=economist.drop(nulls[0])
#print(len(nulls[0]))

nulls=np.where(pd.isnull(cnn['article']))
cnn=cnn.drop(nulls[0])
#print(len(nulls[0]))

nulls=np.where(pd.isnull(reuters['article']))
reuters=reuters.drop(nulls[0])
#print(len(nulls[0]))

#get rid of the city, country '(Reuters) - ' beginnings
for idx in range(len(reuters)):
    current = reuters.loc[idx,'article']
    index=current.find('(Reuters) - ')
    if index != -1:
        reuters.loc[idx,'article']=current[index+len('(Reuters) - '):]

#get rid of the city, country '(CNN)' beginnings
for idx in range(len(cnn)):
    current = cnn.loc[idx,'article']
    index=current.find('(CNN)')
    if index != -1:
        cnn.loc[idx,'article']=current[index+len('(CNN)'):]
    else:
        index=current.find('(CNN Business)')
        if index != -1:
            cnn.loc[idx,'article']=current[index+len('(CNN Business)'):]

#The economist and dailymail don't have these beginnings

#this should have already been done when collecting the articles - maybe the labelling should be done here
reuters = reuters.assign(label=0)
economist = economist.assign(label=1)
cnn = cnn.assign(label=2)
dailymail = dailymail.assign(label=3)

full_dataset=pd.concat([reuters,economist,cnn,dailymail], ignore_index=True)

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