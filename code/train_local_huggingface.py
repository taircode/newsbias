from datasets import (
    load_dataset, 
    load_metric
)
from transformers import (
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
    AutoTokenizer
)
import numpy as np

"""
This is the most basic implementation to fine-tune train a model from_pretrained using the huggingface transformers module.
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
    #initialize the tokenizer and model - using pretrained bert-base-cased
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    model=AutoModelForSequenceClassification.from_pretrained("bert-base-cased",num_labels=4)

    train_dataset = load_dataset('csv', data_files='../articles/train.csv', split='train')
    eval_dataset = load_dataset('csv', data_files='../articles/train.csv', split='train')

    train_encoded=train_dataset.map(tokenize_func, batched=True)
    eval_encoded=eval_dataset.map(tokenize_func, batched=True)

    #randomly select a small subset of data examples for training locally
    train_encoded = train_encoded.shuffle().select(range(10))
    eval_encoded = eval_encoded.shuffle().select(range(5))

    #specify evaluation_strategy if you want the trainer to calculate the compute_metrics function you gave it. 
    #defaults to 'no'. Options are 'no' - no evaluation, 'epoch' - evaluation every epoch, 'steps' - evaluation every 'eval_steps'
    #there are many other hyperparameters one can set, but leaving most as default here
    training_args = TrainingArguments(output_dir="../locally_trained/huggingface",evaluation_strategy='epoch')

    #if you want to compute metrics while training, you need to give the trainer a function that computes metric
    #this is optional, trainer will train without computing metrics if you don't provide compute_metrics
    metric=load_metric("accuracy")
    def my_metrics_func(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return metric.compute(predictions=predictions, references=labels)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_encoded,
        eval_dataset=eval_encoded,
        compute_metrics=my_metrics_func
    )  

    trainer.train()
    trainer.save_model()
