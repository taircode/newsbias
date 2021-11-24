from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import torch
from azureml.core import Workspace

print("Connecting to workspace datastore...")
ws = Workspace.from_config()
ds = ws.get_default_datastore()

print(f"Downloading model to news/model from news/model")
ds.download(
    target_path="/model",
    prefix="news/model/pytorch_model.bin",
    overwrite=False,
    show_progress=True
)
ds.download(
    target_path="/model",
    prefix="news/model/config.json",
    overwrite=False,
    show_progress=True
)
ds.download(
    target_path="/model",
    prefix="news/model/training_args.bin",
    overwrite=False,
    show_progress=True
)

print("Loading model...")
model=AutoModelForSequenceClassification.from_pretrained("./model")
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

#is the entire article a single line? If not, this should probably be readlines()
with open("input_article.txt","r") as file:
    all_lines=file.readlines()
    text_input=' '.join(all_lines)

print("Here is the input text:\n")
print(text_input)

print("Tokenizing input...\n")
tokenized_input=tokenizer(text_input, padding=True, truncation=True,return_tensors="pt")

print(tokenized_input)

#print("Tensorizing input:\n")
#tensor_input=torch.tensor(tokenized_input)

print("Running model to get tokenized output...\n")
output=model(**tokenized_input)
#print(tokenized_output)
#print("\n")
#print(tokenized_output[0])

print(f"output is {output}")
