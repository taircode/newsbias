# newsbias
A classifier model for classifying news articles on a discrete spectrum of factualness. Currently using the following labels with 0 most factual, 3 least factual:

0. Reuters;

1. Economist, New Yorker, National Review;

2. CNN, MNSBC;

3. Dailymail, Fox

Training in Azure cloud cpu-cluster. With more data should switch to gpu. 

Current model is bert-base-cased from pretrained. Add option for other models.


ToDo: Integrate News-API to classifying today's top breaking news articles.
