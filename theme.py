import torch
from pickle import load as pickle_load
from transformers import BertTokenizer
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

themes = {0: "Language", 1: "Geography", 2: "History", 3: "Science", 4: "Biology", 5: "Sport", 6: "Technology",
          7: "Business", 8: "Space", 9: "Art", 10: "Other"}

theme_model = pickle_load(
    open('./new_presentations/static/core/extras/theme_classifier_ml_base.pickle', 'rb'))

bert_model = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(bert_model)

def get_template_category(text):
    test_dataset = [text]

    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=1, collate_fn=pad)

    return test_loop(theme_model, test_loader)

def pad(b):
    v = [tokenizer.encode(x) for x in b]
    l = max(map(len, v))

    return torch.stack(
        [torch.nn.functional.pad(torch.tensor(t), (0, l - len(t)), mode='constant', value=0) for t in v])

def test_loop(model, dataloader):
    model.eval()
    for occurrence in dataloader:
        out = model(occurrence)
        labs = out.logits.argmax(dim=1)
        return labs[0].item()

def calculate_metrics(predictions, true_labels):
    # Calculate precision, recall and f1 score for each class
    accuracy = accuracy_score(true_labels, predictions, normalize=True, sample_weight=None)
    precision = precision_score(true_labels, predictions, average=None, labels=[0,1,2,3,4,5,6,7,8,9,10])
    recall = recall_score(true_labels, predictions, average=None, labels=[0,1,2,3,4,5,6,7,8,9,10])
    f1 = f1_score(true_labels, predictions, average=None, labels=[0,1,2,3,4,5,6,7,8,9,10])
    
    # Return metrics as a dictionary
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }
    
if __name__ == '__main__':
    value_key_map = {}
    predictions = []
    labels = []
    for key, value in themes.items():
        value_key_map[value] = key

    with open('./themes.txt') as f:
        for line in f:
            parts = line.strip().split("|")
            x = get_template_category(line)
            predictions.append(x)
            labels.append(value_key_map[parts[1]])
    
    x = calculate_metrics(predictions, labels)
    print(x)