from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset




if __name__ == "__main__":
    #initialize the tokenizer and model - using pretrained bert-base-cased - see if there's a more specific fine-tuned model in the model database that applies to our task
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    model=AutoModelForSequenceClassification.from_pretrained("bert-base-cased",num_labels=5)

    #This is going to be important - how are you going to classify political bias
    classes=["left","right"]

    dataset = load_dataset('csv', data_files='my_file.csv')

    print(model.config)
    print(model)