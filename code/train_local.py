from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
from datasets import load_dataset
from datasets import Dataset


if __name__ == "__main__":
    #initialize the tokenizer and model - using pretrained bert-base-cased - see if there's a more specific fine-tuned model in the model database that applies to our task
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    model=AutoModelForSequenceClassification.from_pretrained("bert-base-cased",num_labels=4)
    #print(model.config)
    #print(model)

    #This is going to be important - how are you going to classify political bias
    classes=["fact","factual analysis","opinion","selective-incomplete","fiction"]

    train_dataset = load_dataset('csv', data_files='../articles/train.csv', split='train')
    print(f"Train Dataset has length:{len(train_dataset)}\n")

    """note for example this article is too long for default 'max_length' so we need truncation true, or otherwise increase 'max_length'"""
    #print(tokenizer(train_dataset[0]['article'],truncation=True, padding='max_length'))
    #print(train_dataset.column_names)
    print(train_dataset[3376])
    print(train_dataset[3377])
    print(train_dataset[3378])
    
    #add batched=True if you want batching
    encoded_train_dataset = train_dataset.map(lambda examples: tokenizer(examples['article'],truncation=True, padding='max_length'))
    print(encoded_train_dataset)
    #print(encoded_train_dataset.column_names)
    #print(encoded_train_dataset[0])

    #if I don't say split='train' here then it gives me a dictionary of datasets, with split='train' it gives me a dataset
    eval_dataset = load_dataset('csv', data_files='../articles/eval.csv', split='train')
    print(f"Eval Dataset has length:{len(eval_dataset)}\n")
    encoded_eval_dataset = eval_dataset.map(lambda examples: tokenizer(examples['article'],truncation=True, padding='max_length'))

    #do we have to do the following two lines? There's something about huggingface not wanting a column to be called label, so it should be labels
    """seriously, look this up, does this need to be labels."""
    """What's crated here is a dataset with both a 'label' attribute and a 'labels' attribute"""
    encoded_train_dataset = encoded_train_dataset.map(lambda examples: {'labels': examples['label']})
    encoded_eval_dataset = encoded_eval_dataset.map(lambda examples: {'labels': examples['label']})
    #encoded_train_dataset=encoded_train_dataset.set_format(type='torch', columns=['input_ids', 'token_type_ids', 'attention_mask', 'label'])
    #encoded_eval_dataset=encoded_eval_dataset.set_format(type='torch', columns=['input_ids', 'token_type_ids', 'attention_mask', 'label'])

    print("\nDone loading and formatting datasets.\n")

    training_args = TrainingArguments(
        output_dir="../model",
        overwrite_output_dir=True,
        num_train_epochs=3,
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
        train_dataset=encoded_train_dataset,
        eval_dataset=encoded_eval_dataset,
    )  

    print("Training!\n")
    train_result  = trainer.train()
    trainer.save_model()
    print("Done!")