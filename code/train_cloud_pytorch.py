from datasets import (
    load_dataset, 
    load_metric
)
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_scheduler
import torch
import numpy as np
import os
import argparse

#this adds a progress bar while training
from tqdm.auto import tqdm

"""
This is the most basic implementation to fine-tune train a model from_pretrained using huggingface pytorch integration.
Assuming we have data ready to load from a csv.
Reference tutorial: https://huggingface.co/docs/transformers/training
"""

def tokenize_func(example):
    return tokenizer(example['article'],padding='max_length',truncation=True)

#function to inspect the first row of dataset for debugging
def print_single_row_data(data):
    one_row=data.select([0])
    print(one_row)
    for item in one_row:
        print(item)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath")
    parser.add_argument("--output_dir")
    args = parser.parse_args()

    #initialize the tokenizer and model - using pretrained bert-base-cased
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    model=AutoModelForSequenceClassification.from_pretrained("bert-base-cased",num_labels=4)

    train_path = os.path.join(args.datapath,"train.csv")
    eval_path = os.path.join(args.datapath,"eval.csv")

    train_dataset = load_dataset('csv', data_files=train_path, split='train')
    eval_dataset = load_dataset('csv', data_files=eval_path, split='train')

    train_encoded=train_dataset.map(tokenize_func, batched=True)
    eval_encoded=eval_dataset.map(tokenize_func, batched=True)

    train_encoded = train_encoded.remove_columns(['Unnamed: 0', 'article'])
    eval_encoded = eval_encoded.remove_columns(['Unnamed: 0', 'article'])

    #pytorch looks for a column named labels not label
    train_encoded = train_encoded.rename_column('label','labels')
    eval_encoded = eval_encoded.rename_column('label','labels')

    #set format to 'torch' tensors instead of lists - you can also pass tensor='pt' to the tokenizer, but this was giving dimension issues even with padding=True
    train_encoded.set_format('torch')
    eval_encoded.set_format('torch')

    #print_single_row_data(train_encoded)

    #create torch dataloaders from the datasets
    train_dataloader = DataLoader(train_encoded, shuffle=True, batch_size=8)
    eval_dataloader = DataLoader(eval_encoded, batch_size=8)

    #instantiate the optmizier using AdamW from torch.optim
    optimizer = AdamW(model.parameters(), lr=5e-5)

    #instantiate the scheduler from transformers
    num_epochs = 3
    num_training_steps = num_epochs * len(train_dataloader)
    scheduler = get_scheduler(name="linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

    #use a GPU if possible
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(device)
    print(torch.cuda.is_available())
    model.to(device)

    #instantiate progress bar from tqdm.auto
    progress_bar = tqdm(range(num_training_steps))

    model.train()
    for epoch in range(num_epochs):
        for batch in train_dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()

            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
            progress_bar.update(1)

    #if you want to compute metrics while training, you need to write a loop to accumulate all the batches with add_batch
    #this is optional, model.train() will train without computing metrics
    metric = load_metric("accuracy")
    model.eval()
    for batch in eval_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        with torch.no_grad():
            outputs = model(**batch)

        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)
        metric.add_batch(predictions=predictions, references=batch["labels"])

    metric.compute()

    model.save_pretrained(save_directory=args.output_dir)