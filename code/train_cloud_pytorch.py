from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
from datasets import load_dataset
from transformers.integrations import MLflowCallback
import argparse
import os
import pandas as pd
from myDataset import myDataset
import nltk

#This is the training script to be uploaded to Azure

def get_chunks(longlist):
    #you should probably pad the last chunk or maybe just ignore chunks that are way too small
    for i in range(0, len(longlist), 512):
        yield longlist[i:i + 512]

#you should probably pad the last chunk or maybe just ignore chunks that are way too small
def chop_article(token_list, tokenizer, token_types, attention_mask):
    token_list=token_list[1:len(token_list)-1]
    #print(token_list)
    text=tokenizer.decode(token_list)
    #use this to turn text into list of sentences
    text_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences=text_tokenizer.tokenize(text)
    start_indices=[0]
    global_index=0
    local_count=0
    for i, sentence in enumerate(sentences):
        #print(sentence)
        encoded_sentence=tokenizer.encode(sentence)
        #print(encoded_sentence)
        #print(len(encoded_sentence))
        #print('\n')
        cur_len=len(encoded_sentence)-2 #note that encode gives a start symbol (101) and end symbol (102)
        local_count=local_count+cur_len
        if local_count>510:
            start_indices.append(global_index)
            local_count=cur_len
        global_index=global_index+cur_len
    start_indices.append(len(token_list))
    article_chunks=[]
    type_chunks=[]
    mask_chunks=[]
    for i in range(len(start_indices)-1):
        article_chunks.append(token_list[start_indices[i]:start_indices[i+1]])
        article_chunks[i].insert(0, 101)
        article_chunks[i].append(102)
        article_chunks[i].extend([0]*(512-len(article_chunks[i])))
        #print(f"length of article chunk is {len(article_chunks[i])}")
        type_chunks.append(token_types[start_indices[i]:start_indices[i+1]])
        type_chunks[i].insert(0, 0)
        type_chunks[i].append(0)
        type_chunks[i].extend([0]*(512-len(type_chunks[i])))
        #print(f"length of type chunk is {len(type_chunks[i])}")
        mask_chunks.append(attention_mask[start_indices[i]:start_indices[i+1]])
        mask_chunks[i].insert(0, 1)
        mask_chunks[i].append(1)
        mask_chunks[i].extend([0]*(512-len(mask_chunks[i])))
        #print(f"length of type chunk is {len(type_chunks[i])}")
    return article_chunks, type_chunks, mask_chunks


if __name__ == "__main__":
    nltk.download('punkt')

    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath")
    parser.add_argument("--output_dir")
    args = parser.parse_args()

    #initialize the tokenizer and model - using pretrained bert-base-cased - see if there's a more specific fine-tuned model in the model database that applies to our task
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    model=AutoModelForSequenceClassification.from_pretrained("bert-base-cased",num_labels=4)

    #This is going to be important - how are you going to classify political bias
    classes=["fact","factual analysis","opinion","selective-incomplete","fiction"]

    train_path = os.path.join(args.datapath,"train.csv")
    eval_path = os.path.join(args.datapath,"eval.csv")

    train_data = load_dataset('csv', data_files=train_path, split='train')
    eval_data = load_dataset('csv', data_files=eval_path, split='train')

    X_train = list(train_data['article'])
    y_train = list(train_data['label'])
    print(f"Train Dataset has length:{len(X_train)}\n")
    X_eval = list(eval_data['article'])
    y_eval = list(eval_data['label'])
    print(f"Eval Dataset has length:{len(X_eval)}\n")

    #note, turning the tokens into torch tensors in the myDataset class
    X_train_encoded=tokenizer(X_train,truncation=False, padding='max_length')
    X_eval_encoded=tokenizer(X_eval,truncation=False, padding='max_length')

    idx=0
    while idx<len(X_train_encoded['input_ids']):
        #print("in while")
        #print(idx)
        #print(f"input_ids has length {len(X_train_encoded['input_ids'])}")
        num_tokens=len(X_train_encoded['input_ids'][idx])
        #print(f"num_tokens is {num_tokens}")
        if num_tokens>512:
            long_text=X_train_encoded['input_ids'][idx]
            token_types=X_train_encoded['token_type_ids'][idx]
            attention_mask=X_train_encoded['attention_mask'][idx]
            article_chunks, type_chunks, mask_chunks=chop_article(long_text,tokenizer,token_types,attention_mask)
            del X_train_encoded['input_ids'][idx]
            X_train_encoded['input_ids'][idx:idx]=article_chunks
            y_label=y_train[idx]
            y_train[idx:idx]=[y_label]*len(article_chunks)
            del X_train_encoded['token_type_ids'][idx]
            X_train_encoded['token_type_ids'][idx:idx]=type_chunks
            del X_train_encoded['attention_mask'][idx]
            X_train_encoded['attention_mask'][idx:idx]=mask_chunks
            idx=idx+len(article_chunks)
        else:
            idx=idx+1

    for i in range(len(X_train_encoded['input_ids'])):
        print(len(X_train_encoded['input_ids'][i]))

    #break up the long articles in eval set
    idx=0
    while idx<len(X_eval_encoded['input_ids']):
        #print("in while")
        #print(idx)
        #print(f"input_ids has length {len(X_train_encoded['input_ids'])}")
        num_tokens=len(X_eval_encoded['input_ids'][idx])
        #print(f"num_tokens is {num_tokens}")
        if num_tokens>512:
            long_text=X_eval_encoded['input_ids'][idx]
            token_types=X_eval_encoded['token_type_ids'][idx]
            attention_mask=X_eval_encoded['attention_mask'][idx]
            article_chunks, type_chunks, mask_chunks=chop_article(long_text,tokenizer,token_types,attention_mask)
            del X_eval_encoded['input_ids'][idx]
            X_eval_encoded['input_ids'][idx:idx]=article_chunks
            y_label=y_eval[idx]
            y_eval[idx:idx]=[y_label]*len(article_chunks)
            del X_eval_encoded['token_type_ids'][idx]
            X_eval_encoded['token_type_ids'][idx:idx]=type_chunks
            del X_eval_encoded['attention_mask'][idx]
            X_eval_encoded['attention_mask'][idx:idx]=mask_chunks
            idx=idx+len(article_chunks)
        else:
            idx=idx+1

    for i in range(len(X_eval_encoded['input_ids'])):
        print(len(X_eval_encoded['input_ids'][i]))

    train_dataset=myDataset(X_train_encoded,y_train)
    eval_dataset=myDataset(X_eval_encoded,y_eval)

    print("\nDone loading and formatting datasets.\n")

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        overwrite_output_dir=True,
        num_train_epochs=1,
        learning_rate=1e-5,
        weight_decay=0.01,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        evaluation_strategy="epoch", #or change to steps and set eval_steps=int (default=logging_steps)
        logging_strategy="epoch", #or change to steps and set logging_steps=int (default=500)
        logging_dir='./logs',
        logging_steps=500,
        save_strategy="epoch", #or change to steps and set save_steps=int (default=500)
    )

    print("\nSpecified Training Args.\n")

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )  

    print("\nInstantiated Trainer.\n")

    #what does this do? Look it up
    trainer.pop_callback(MLflowCallback)

    print("Training!\n")
    train_result  = trainer.train()
    trainer.save_model()
    print("Done!")