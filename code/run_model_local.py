import pandas as pd
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import argparse
import torch.nn
import torch
import numpy as np

#if you want to just look at one article
def single_article(filename):
    with open("../articles_test/"+filename,"r") as file:
        all_lines=file.readlines()
        text_input=' '.join(all_lines)

    print("Here is the input text:\n")
    print(text_input)

    print("Tokenizing input...\n")
    tokenized_input=tokenizer(text_input, padding=True, truncation=True, return_tensors="pt")

    print("Running model to get tokenized output...\n")
    with torch.no_grad():
        output=model(**tokenized_input)
    logits=output.logits
    print(f"logits are {logits}")

    soft_func=torch.nn.Softmax(dim=1)
    softmax=soft_func(logits)
    print(f"softmax is {softmax}")

    prediction = np.argmax(logits)
    print(f"Prediction is {prediction}")

parser = argparse.ArgumentParser()
parser.add_argument("--type","-t",choices=["huggingface","pytorch"],default='huggingface',help="select training framework") #huggingface or pytorch
parser.add_argument("--test_article","-art",default='all',help="select a single filename to test or 'all' for entire eval dataset") #huggingface or pytorch
args = parser.parse_args()

path="../locally_trained/"+args.type

print("Loading "+args.type+" trained model...")
model=AutoModelForSequenceClassification.from_pretrained(path)
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

#if you want to just test a single article
if args.test_article!='all':
    single_article(args.test_article)
else:
    eval=pd.read_csv("../articles/eval.csv", usecols=['article','label'])
    model.eval()
    for id in range(len(eval)):
        text=eval.loc[id,'article']
        label=eval.loc[id,'label']

        tokenized_text=tokenizer(text, padding=True, truncation=True, return_tensors="pt")
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