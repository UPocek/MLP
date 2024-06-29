# Just for testing

import torch
from pickle import load as pickle_load
from transformers import pipeline, BertTokenizer, BartForConditionalGeneration
from sklearn.metrics import precision_score, recall_score, f1_score

importance_model = pickle_load(
    open('./new_presentations/static/core/extras/importance_classifier_ml_base.pickle', 'rb'))

bert_model = 'bert-base-uncased'

tokenizer = BertTokenizer.from_pretrained(bert_model)

summarize_model = BartForConditionalGeneration.from_pretrained(
    'sshleifer/distilbart-cnn-12-6')

def classify(text, topic, num_paragraphs):
    test_dataset = []

    for section in text:
        test_dataset.append(topic + ' ' + section)

    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=num_paragraphs, collate_fn=pad)

    return test_loop(importance_model, test_loader)


def pad(b):
    v = [tokenizer.encode(x) for x in b]
    l = max(map(len, v))

    return torch.stack(
        [torch.nn.functional.pad(torch.tensor(t), (0, l - len(t)), mode='constant', value=0) for t in v])


def test_loop(model, texts):
    model.eval()

    for text in texts:
        out = model(text)
        labs = out.logits.argmax(dim=1)
        return labs + 1

def calculate_metrics(predictions, true_labels):
    # Calculate precision, recall and f1 score for each class
    precision = precision_score(true_labels, predictions, average=None, labels=[1, 2, 3])
    recall = recall_score(true_labels, predictions, average=None, labels=[1, 2, 3])
    f1 = f1_score(true_labels, predictions, average=None, labels=[1, 2, 3])
    
    # Return metrics as a dictionary
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }

if __name__ == '__main__':
    predictions = []
    labels = []
    with open('./texts.txt', 'r') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) != 2:
                continue
            prediction = classify(parts[0], parts[0].split(" ")[0], 1)
            predictions.append(prediction.item())
            labels.append(int(parts[1]))
    
    x = calculate_metrics(predictions, labels)
    print(x)
            
