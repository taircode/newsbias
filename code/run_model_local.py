import pandas as pd
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)


print("Loading model...")
model=AutoModelForSequenceClassification.from_pretrained("../locally_trained/huggingface")
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

eval=pd.read_csv("../articles/eval.csv", usecols=['article','label'])
for id in range(len(eval)):
    text=eval.loc[id,'article']
    label=eval.loc[id,'label']

    tokenized_text=tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    output=model(**tokenized_text)
    print(f"output is {output}")
    print(f"SoftMax is {F.softmax(output[0],dim=1)}")
    print(f"Actual label was {label}")