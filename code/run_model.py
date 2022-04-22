from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import pandas as pd
import torch.nn.functional as F
#from scipy.special import softmax
import torch
from azureml.core import Workspace

print("Connecting to workspace datastore...")
ws = Workspace.from_config()
ds = ws.get_default_datastore()

print(f"Downloading config.json to local news/model from news/model")
ds.download(
    target_path="..",
    prefix="news/model/config.json",
    overwrite=False,
    show_progress=True
)
print(f"Downloading training_args.bin to local news/model from news/model")
ds.download(
    target_path="..",
    prefix="news/model/training_args.bin",
    overwrite=False,
    show_progress=True
)
print(f"Downloading pytorch_model.bin to local news/model from news/model")
ds.download(
    target_path="..",
    prefix="news/model/pytorch_model.bin",
    overwrite=False,
    show_progress=True
)

print("Loading model...")
model=AutoModelForSequenceClassification.from_pretrained("../news/model")
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

#is the entire article a single line? If not, this should probably be readlines()
with open("../articles_test/ap_article.txt","r") as file:
    all_lines=file.readlines()
    text_input=' '.join(all_lines)

print("Here is the input text:\n")
print(text_input)

print("Tokenizing input...\n")

tokenized_input=tokenizer(text_input, padding=True, truncation=True, return_tensors="pt")
print(tokenized_input)

print("Running model to get tokenized output...\n")
output=model(**tokenized_input)
#print(tokenized_output)
#print("\n")
#print(tokenized_output[0])

print(f"output is {output}")
print(f"SoftMax is {F.softmax(output[0],dim=-1)}")
#print(f"softmax is {softmax(output)}")


eval=pd.read_csv("../articles/eval.csv", usecols=['article','label'])
for id in range(len(eval)):
    text=eval.loc[id,'article']
    label=eval.loc[id,'label']

    tokenized_text=tokenizer(text, padding=True, truncation=True,return_tensors="pt")
    output=model(**tokenized_text)
    print(f"output is {output}")
    print(f"SoftMax is {F.softmax(output[0],dim=1)}")
    print(f"Actual label was {label}")