import pandas as pd
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import argparse
import torch.nn.functional as F
import torch

parser = argparse.ArgumentParser()
parser.add_argument("--type","-t",choices=["huggingface","pytorch"],default='huggingface',help="select training framework") #huggingface or pytorch
args = parser.parse_args()

print("Loading "+args.type+" trained model...")
model=AutoModelForSequenceClassification.from_pretrained("../locally_trained/"+args.type)
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
    softmax=F.softmax(output[0],dim=1)
    print(max(softmax))
    print(f"output is {max(output[0])}")
    print(f"SoftMax is {softmax}")
    print(f"Prediction is {output[0]}")
    print(f"Actual label was {label}")