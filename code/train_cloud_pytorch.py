from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
from transformers.integrations import MLflowCallback
import argparse
import os
import pandas as pd
from myDataset import myDataset

#This is the training script to be uploaded to Azure

if __name__ == "__main__":
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

    train_data=pd.read_csv(train_path)
    X_train = list(train_data['article'])
    y_train = list(train_data['label'])

    print(f"Train Dataset has length:{len(X_train)}\n")

    eval_data=pd.read_csv(eval_path)
    X_eval = list(eval_data['article'])
    y_eval = list(eval_data['label'])

    print(f"Eval Dataset has length:{len(X_eval)}\n")

    #note, turning the tokens into torch tensors in the myDataset class
    X_train_encoded=tokenizer(X_train,truncation=True, padding='max_length')
    X_eval_encoded=tokenizer(X_eval,truncation=True, padding='max_length')

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
        logging_steps=1000,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )  

    #what does this do? Look it up
    trainer.pop_callback(MLflowCallback)

    print("Training!\n")
    train_result  = trainer.train()
    trainer.save_model()
    print("Done!")