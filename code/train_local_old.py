from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
from datasets import load_dataset
from datasets import Dataset

import torch

from datasets import Value, Sequence, Features

"""
Was having an issue with this way of training - when calling dataset.map with return_tensors='pt' kept returning a list, not a pt-tensor.
"""

if __name__ == "__main__":
    #initialize the tokenizer and model - using pretrained bert-base-cased
    #see if there's a more specific fine-tuned model in the model database that applies to our task
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    model=AutoModelForSequenceClassification.from_pretrained("bert-base-cased",num_labels=4)
    #print(model.config)
    #print(model)

    #This is going to be important - how are you going to classify political bias
    classes=["fact","factual analysis","opinion","selective-incomplete","fiction"]

    #here you could have just loaded the csv as a dictionary and then create dataset from dict after tokenizing
    train_dataset = load_dataset('csv', data_files='../articles/train.csv', split='train')
    print(f"Train Dataset has length:{len(train_dataset)}\n")
    #print(train_dataset)

    """note that some articles are too long for default 'max_length' so we need truncation true, or otherwise increase 'max_length'"""
    #print(tokenizer(train_dataset[0]['article'],truncation=True, padding='max_length'))
    #print(train_dataset.column_names)
    #print(train_dataset[3376])

    #features = Features({
    #    "label": Sequence(Value("int32")),
    #    "sembedding": Sequence(Value("float32"))
    #})
    
    #add batched=True if you want batching

    #mylist = []
    #for example in train_dataset:
    #    processed_example = tokenizer(example['article'], truncation=True, padding='max_length',return_tensors="pt")
    #    example.update(processed_example)
    #    mylist.append(example)
    #print(mylist)
    #exit()
    #encoded_train_dataset=load_dataset(mylist)
    #exit()

    encoded_train_dataset = train_dataset.map(lambda examples: tokenizer(examples['article'],truncation=True, padding='max_length',return_tensors="pt"), batched=False)
    encoded_train_dataset = encoded_train_dataset.map(lambda examples: {'labels': examples['label']})
    #encoded_train_dataset.set_format(type='torch', columns=['input_ids', 'token_type_ids', 'attention_mask','labels'])
    #print(encoded_train_dataset)
    #print(encoded_train_dataset.column_names)
    #print(encoded_train_dataset[0])

    #if I don't say split='train' here then it gives me a dictionary of datasets, with split='train' it gives me a dataset
    eval_dataset = load_dataset('csv', data_files='../articles/eval.csv', split='train')
    #print(eval_dataset)
    #print(eval_dataset[0])
    print(f"Eval Dataset has length:{len(eval_dataset)}\n")

    encoded_eval_dataset = eval_dataset.map(lambda examples: tokenizer(examples['article'],truncation=True, padding='max_length',return_tensors="pt"), batched=False)
    print(encoded_eval_dataset)
    encoded_eval_dataset = encoded_eval_dataset.map(lambda examples: {'labels': examples['label']})
    print(encoded_eval_dataset)
    encoded_eval_dataset.set_format('torch', columns=['input_ids', 'token_type_ids', 'attention_mask','labels'])
    print(encoded_eval_dataset)
    #print(encoded_eval_dataset['article'])
    print("BEFORE LONG LIST")
    print(encoded_eval_dataset['label'][0])
    #print(encoded_eval_dataset['article'][0])
    #print(encoded_eval_dataset['input_ids'][0])
    print(type(encoded_eval_dataset['article'][0]))
    print(type(encoded_eval_dataset['input_ids'][0]))
    print(type(encoded_eval_dataset['token_type_ids'][0]))
    print(type(encoded_eval_dataset['attention_mask'][0]))
    print(type(encoded_eval_dataset['labels'][0]))
    print(encoded_eval_dataset['labels'][0].dtype())

    #feats = encoded_eval_dataset.features.copy()
    #feats['labels'].feature = Value(dtype='int32')
    #feats = Features(feats)
    #encoded_eval_dataset.cast(feats)

    #feats = encoded_train_dataset.features.copy()
    #feats['labels'].feature = Value(dtype='int32')
    #feats = Features(feats)
    #encoded_train_dataset.cast(feats)

    print("After case LONG LIST")
    print(encoded_eval_dataset['label'][0])
    #print(encoded_eval_dataset['article'][0])
    #print(encoded_eval_dataset['input_ids'][0])
    print(type(encoded_eval_dataset['article'][0]))
    print(type(encoded_eval_dataset['input_ids'][0]))
    print(type(encoded_eval_dataset['token_type_ids'][0]))
    print(type(encoded_eval_dataset['attention_mask'][0]))
    print(type(encoded_eval_dataset['labels'][0]))
    print(encoded_eval_dataset['labels'][0].type())

    print("LAST")
    #print(encoded_eval_dataset[23])
    #print(encoded_eval_dataset['labels'][0].type())
    #print(encoded_eval_dataset[0])
    #print(encoded_eval_dataset[0]['input_ids'][0][0])
    #print(type(encoded_eval_dataset[0]['input_ids'][0][0]))
    #exit()

    #do we have to do the following two lines? There's something about huggingface not wanting a column to be called label, so it should be labels
    """seriously, look this up, does this need to be labels?"""
    """What's crated here is a dataset with both a 'label' attribute and a 'labels' attribute"""
    #encoded_train_dataset = encoded_train_dataset.map(lambda examples: {'labels': examples['label']})
    #encoded_eval_dataset = encoded_eval_dataset.map(lambda examples: {'labels': examples['label']})
    #encoded_train_dataset.set_format(type='torch', columns=['input_ids', 'token_type_ids', 'attention_mask', 'label'])
    #encoded_eval_dataset.set_format(type='torch', columns=['input_ids', 'token_type_ids', 'attention_mask', 'label'])

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
        train_dataset=encoded_train_dataset,
        eval_dataset=encoded_eval_dataset,
        #tokenizer=tokenizer
    )  

    print("Training!\n")
    train_result  = trainer.train()
    trainer.save_model()
    print("Done!")