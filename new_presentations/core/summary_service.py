import torch
from pickle import load as pickle_load
from transformers import pipeline, BertTokenizer, BartForConditionalGeneration

importance_model = pickle_load(
    open('static/core/extras/importance_classifier_ml_base.pickle', 'rb'))

bert_model = 'bert-base-uncased'

tokenizer = BertTokenizer.from_pretrained(bert_model)

summarize_model = BartForConditionalGeneration.from_pretrained(
    'sshleifer/distilbart-cnn-12-6')


def summarize_text(text, number_of_slides, title, min_words_per_slide, max_words_per_slide):
    offset = 2  # due to welcome and thank you slides

    min_number_of_slides_requested, max_number_of_slides_requested, true_number_of_slides = calculate_min_max(
        number_of_slides, text, offset)

    if true_number_of_slides > max_number_of_slides_requested - offset:
        remove_least_relevante(text, title, true_number_of_slides,
                               min_number_of_slides_requested, max_number_of_slides_requested, offset)

    final_text = sum_sequential(text, min_words_per_slide, max_words_per_slide)

    return final_text


def calculate_min_max(num_slides, text, offset):
    true_number_of_slides = 0
    max_number_of_slides_supported = 20

    for section in text:
        true_number_of_slides += len(text[section])

    try:
        min_n, max_n = num_slides.strip().split('-')
        min_n, max_n = int(min_n), int(max_n)
        return min_n, max_n, true_number_of_slides
    except Exception:
        return min(true_number_of_slides + offset, max_number_of_slides_supported - offset), min(true_number_of_slides + offset,
                                                                                                 max_number_of_slides_supported), true_number_of_slides


def remove_least_relevante(text, title, true_number_of_slides, min_number_of_slides_requested, max_number_of_slides_requested, offset):
    low_relevance, medium_relevance, high_relevance = 3, 2, 1
    temp = []

    arr, ones, twos, threes = classify(
        text, title, true_number_of_slides)

    # Summary should always be high_relevance (fixing AI's inconsistency)
    if arr[0][1] != high_relevance:
        if arr[0][1] == medium_relevance:
            twos -= 1
        else:
            threes -= 1
        arr[0][1] = high_relevance
        ones += 1

    if ones >= min_number_of_slides_requested:
        for a in arr:
            if a[1] != high_relevance:
                t = a[0].split('|')
                del text[t[0]][t[1]]
                if not text[t[0]]:
                    del text[t[0]]
            else:
                temp.append(a[0])
        while ones > max_number_of_slides_requested - offset:
            ones -= 1
            t = temp.pop(-1).split('|')
            del text[t[0]][t[1]]
            if not text[t[0]]:
                del text[t[0]]
    elif ones + twos >= min_number_of_slides_requested:
        x = ones + twos
        for a in arr:
            if a[1] == low_relevance:
                t = a[0].split('|')
                del text[t[0]][t[1]]
                if not text[t[0]]:
                    del text[t[0]]
            else:
                temp.append(a[0])
        while x > max_number_of_slides_requested - offset:
            x -= 1
            t = temp.pop(-1).split('|')
            del text[t[0]][t[1]]
            if not text[t[0]]:
                del text[t[0]]
    else:
        x = ones + twos + threes
        i = -1
        while x > max_number_of_slides_requested - offset:
            if arr[i][1] == low_relevance:
                t = arr[i][0].split('|')
                del text[t[0]][t[1]]
                if not text[t[0]]:
                    del text[t[0]]
                x -= 1
            i -= 1


def sum_sequential(text_for_summarization, min_words, max_words):
    absolute_max_words_per_slide = 140
    tolerable_excess = 1.4

    summarizer = pipeline(
        'summarization', model='sshleifer/distilbart-cnn-12-6')

    for section in text_for_summarization:
        for paragraph in text_for_summarization[section]:
            content = text_for_summarization[section][paragraph]
            number_of_words = len(content.split())
            if number_of_words > max_words * tolerable_excess or number_of_words > absolute_max_words_per_slide:
                text_for_summarization[section][paragraph] = sum_with_pipline(summarizer,
                                                                              content, min_words, max_words)

    return text_for_summarization


def sum_with_pipline(summarizer, text_for_summarization, min_words, max_words):
    try:
        pipline_summary = summarizer(text_for_summarization, max_length=max_words, min_length=min_words,
                                     do_sample=False)
    except Exception:
        passed = False
        sub = 0
        while not passed:
            sub += 0.2
            try:
                pipline_summary = summarizer(text_for_summarization[:int(len(text_for_summarization) * (1 - sub))],
                                             max_length=max_words,
                                             min_length=min_words, do_sample=False)
                passed = True
            except Exception:
                pass

    return pipline_summary[0]['summary_text']


def classify(text, topic, num_paragraphs):
    test_dataset = []
    content_parts = []

    for section in text:
        for sub_section in text[section]:
            test_dataset.append(topic + ' ' + section + ' ' + sub_section)
            content_parts.append(section + '|' + sub_section)

    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=num_paragraphs, collate_fn=pad)

    return test_loop(importance_model, test_loader, content_parts)


def pad(b):
    v = [tokenizer.encode(x) for x in b]
    l = max(map(len, v))

    return torch.stack(
        [torch.nn.functional.pad(torch.tensor(t), (0, l - len(t)), mode='constant', value=0) for t in v])


def test_loop(model, dataloader, content_parts):
    model.eval()
    predictions = []
    ones, twos, threes = 0, 0, 0

    for texts in dataloader:
        out = model(texts)
        labs = out.logits.argmax(dim=1)
        for i, label in enumerate(labs):
            label += 1
            if label == 1:
                ones += 1
            elif label == 2:
                twos += 1
            else:
                threes += 1
            predictions.append([content_parts[i], label.item()])

    return predictions, ones, twos, threes
