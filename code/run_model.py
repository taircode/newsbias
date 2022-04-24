from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import pandas as pd
import torch.nn.functional as F
#from scipy.special import softmax
import torch
from azureml.core import Workspace
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--type","-t",choices=["huggingface","pytorch"],default='huggingface',help="select training framework") #huggingface or pytorch
parser.add_argument("--overwrite","-o",choices=['True','False'],default='False',help='overwrite local copy of model if True')
args = parser.parse_args()

overwrite=True if args.overwrite=='True' else False
location='news/model/'+args.type

print("Connecting to workspace datastore...")
ws = Workspace.from_config()
ds = ws.get_default_datastore()

print(f"Downloading config.json to local {location} from datastore {location}")
ds.download(
    target_path="..",
    prefix=location+"/config.json",
    overwrite=overwrite,
    show_progress=True
)
print(f"Downloading training_args.bin to local {location} from datastore {location}")
ds.download(
    target_path="..",
    prefix=location+"/training_args.bin",
    overwrite=overwrite,
    show_progress=True
)
print(f"Downloading pytorch_model.bin to local {location} from datastore {location}")
ds.download(
    target_path="..",
    prefix=location+"/pytorch_model.bin",
    overwrite=overwrite,
    show_progress=True
)

print("Loading model...")
model=AutoModelForSequenceClassification.from_pretrained("../"+location)
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

eval=pd.read_csv("../articles/eval.csv", usecols=['article','label'])
for id in range(len(eval)):
    text=eval.loc[id,'article']
    label=eval.loc[id,'label']

    tokenized_text=tokenizer(text, padding=True, truncation=True,return_tensors="pt")
    
    with torch.no_grad():
        output=model(**tokenized_text)

    logits = output.logits

    soft_func=torch.nn.Softmax(dim=1)
    softmax=soft_func(logits)

    prediction = np.argmax(logits, axis=-1)

    #print(f"logits are {logits}")
    #print(f"softmax is {softmax}")
    print(f"Prediction is {prediction}")
    print(f"Actual label was {label}")

#if you want to just look at one article
#with open("../articles_test/ap_article.txt","r") as file:
#    all_lines=file.readlines()
#    text_input=' '.join(all_lines)

#print("Here is the input text:\n")
#print(text_input)

#print("Tokenizing input...\n")

#tokenized_input=tokenizer(text_input, padding=True, truncation=True, return_tensors="pt")
#print(tokenized_input)

#print("Running model to get tokenized output...\n")
#output=model(**tokenized_input)

#print(f"output is {output}")
#print(f"SoftMax is {torch.nn.Softmax(output[0],dim=-1)}")