from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import pandas as pd
from myDataset import myDataset

def get_chunks(longlist):
    for i in range(0, len(longlist), 512):
        yield longlist[i:i + 512]

if __name__ == "__main__":
    #initialize the tokenizer and model - using pretrained bert-base-cased - see if there's a more specific fine-tuned model in the model database that applies to our task
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
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

    #break up the long articles in training set
    for i in range(len(X_train)):
        num_tokens=len(X_train_encoded['input_ids'][i])
        if num_tokens>512:
            article_chunks=list(get_chunks(longlist=X_train_encoded['input_ids'][i]))
            type_chunks=list(get_chunks(longlist=X_train_encoded['token_type_ids'][i]))
            mask_chunks=list(get_chunks(longlist=X_train_encoded['attention_mask'][i]))
            X_train_encoded['input_ids'][i:i]=list(article_chunks)
            y_label=y_train[i]
            y_train[i:i]=[y_label]*len(article_chunks)
            X_train_encoded['token_type_ids'][i:i]=list(type_chunks)
            X_train_encoded['attention_mask'][i:i]=list(mask_chunks)

    #break up the long articles in eval set
    for i in range(len(X_eval)):
        num_tokens=len(X_eval_encoded['input_ids'][i])
        if num_tokens>512:
            article_chunks=list(get_chunks(longlist=X_eval_encoded['input_ids'][i]))
            type_chunks=list(get_chunks(longlist=X_eval_encoded['token_type_ids'][i]))
            mask_chunks=list(get_chunks(longlist=X_eval_encoded['attention_mask'][i]))
            X_eval_encoded['input_ids'][i:i]=list(article_chunks)
            y_label=y_eval[i]
            y_eval[i:i]=[y_label]*len(article_chunks)
            X_eval_encoded['token_type_ids'][i:i]=list(type_chunks)
            X_eval_encoded['attention_mask'][i:i]=list(mask_chunks)

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

