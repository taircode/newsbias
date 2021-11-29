from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import pandas as pd
from myDataset import myDataset

import nltk.data

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
    #initialize the tokenizer and model - using pretrained bert-base-cased - see if there's a more specific fine-tuned model in the model database that applies to our task
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

    #trial_text="I asked McFadden if it was frustrating to stick to such a cautious script, even while the world had moved on. “ It ’ s just a recognition of where we are, ” he said. “ Economic assumptions have changed over the past decade. They definitely have, and we understand that. But the task of winning people ’ s trust is still there. ” You can see history passing the Party by. Since Labour lost power, British politics has undergone two great upheavals — Brexit and the rise of Scottish nationalism — both of which have been motivated by questions of identity and belonging. Labour has yet to formulate a convincing response to either. In “ The Road Ahead, ” Starmer acknowledged the skill of the Conservatives in riding these changes. “ The strength of the Tory party is in no small part due to its ability to shed its skin, ” he wrote. Embracing Brexit and falling in behind the chummy nationalism of Johnson, the Conservatives have managed to assemble a broad but fragile coalition that stretches from wealthy, tax - shy commuters in the London suburbs to postindustrial communities in the English northwest, who are crying out for investment and support. Labour, by contrast, doesn ’ t seem to know which way to turn — even though millions of voters seem to have already made up their minds."
    #print(trial_text)
    #encoded_text=tokenizer.encode(trial_text)
    #print(encoded_text)
    #raw=tokenizer.decode(encoded_text)
    #print(raw)
    
    #use this to turn text into list of sentences
    #text_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    #sentences=text_tokenizer.tokenize(raw)
    #for sentence in sentences:
    #    print(sentence)
    #    encoded_sentence=tokenizer.encode(sentence)
    #    print(encoded_sentence)
    #exit()

    model=AutoModelForSequenceClassification.from_pretrained("bert-base-cased",num_labels=4)

    print("\nLoading datasets.\n")

    train_data=pd.read_csv("../articles/train.csv")
    X_train = list(train_data['article'])
    y_train = list(train_data['label'])
    
    print(f"Train dataset has {len(X_train)} articles.\n")

    eval_data=pd.read_csv("../articles/eval.csv")
    X_eval = list(eval_data['article'])
    y_eval = list(eval_data['label'])

    print(f"Eval dataset has {len(X_eval)} articles.\n")

    #note, turning the tokens into torch tensors in the myDataset class
    X_train_encoded=tokenizer(X_train,truncation=False, padding='max_length')
    X_eval_encoded=tokenizer(X_eval,truncation=False, padding='max_length')

    #print(len(X_train_encoded['input_ids'][0]))
    #print(type(X_train_encoded))
    #print(type(X_train_encoded['input_ids']))

    #use this to turn text into list of sentences
    #text_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    #break up the long articles in training set
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

    #wrap BatchEncoding as a torch.util dataset
    train_dataset=myDataset(X_train_encoded,y_train)
    eval_dataset=myDataset(X_eval_encoded,y_eval)

    print("\nDone loading and formatting datasets.\n")

    training_args = TrainingArguments(
        output_dir="../model",
        overwrite_output_dir=True,
        num_train_epochs=1,
        learning_rate=1e-5,
        weight_decay=0.01,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        evaluation_strategy="steps",
        logging_dir='./logs',
        logging_steps=100
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )  

    print("Training!\n")
    train_result  = trainer.train()
    trainer.save_model()
    print("Done!")

