import pandas as pd
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import argparse
import torch.nn
import torch
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("--type","-t",choices=["huggingface","pytorch"],default='huggingface',help="select training framework") #huggingface or pytorch
args = parser.parse_args()

path="../locally_trained/"+args.type

print("Loading "+args.type+" trained model...")
model=AutoModelForSequenceClassification.from_pretrained(path)
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")


eval=pd.read_csv("../articles/eval.csv", usecols=['article','label'])
model.eval()
for id in range(len(eval)):
    text=eval.loc[id,'article']
    label=eval.loc[id,'label']

    tokenized_text=tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        output=model(**tokenized_text)

    logits = output.logits
    softmax=torch.nn.Softmax(logits)
    prediction = np.argmax(logits, axis=-1)

    #print(f"output is {max(output[0])}")
    #print(f"SoftMax is {softmax}")
    print(f"Prediction is {prediction}")
    print(f"Actual label was {label}")