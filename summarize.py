from pickle import load as pickle_load
from transformers import pipeline, BertTokenizer, BartForConditionalGeneration
import wikipedia
import wikipediaapi
from re import sub as re_sub, split as re_split
from copy import deepcopy
from rouge_score import rouge_scorer
import json

importance_model = pickle_load(
    open('./new_presentations/static/core/extras/importance_classifier_ml_base.pickle', 'rb'))

bert_model = 'bert-base-uncased'

tokenizer = BertTokenizer.from_pretrained(bert_model)

summarize_model = BartForConditionalGeneration.from_pretrained(
    'sshleifer/distilbart-cnn-12-6')

def find_url(title, language):
    wiki = wikipediaapi.Wikipedia('en')

    page = wiki.page(title)

    return page.fullurl, page.summary, page.sections, page.title


def create_content_tree(summary, sections, title):
    text_tree_basis = {'About the ' + title: str(summary)}

    filled_text_tree = create_tree_from_sections(
        sections, text_tree_basis, title)

    return filled_text_tree


def create_tree_from_sections(section, tree, title):
    add_main_topics_to_tree(section, tree)

    add_sub_topics_to_main_topics(tree)

    return compress_tree(tree, title)


def add_main_topics_to_tree(sections, tree):
    for paragraph in sections:
        paragraph = str(paragraph).split(' (1):\n')
        tree[paragraph[0].replace('Section: ', '')] = paragraph[1]

    remove_useless_paragraphs(tree)


def add_sub_topics_to_main_topics(tree):
    for main_title in tree:
        content = re_sub(
            'Subsections \(\d{1}\):\n', '', tree[main_title]).split('Section: ')
        tree[main_title] = {'major subject': clean_text(content.pop(0))}
        for paragraph in content:
            sub_theme, sub_content = re_split(' \(\d{1}\):\n', paragraph)
            tree[main_title][sub_theme] = clean_text(sub_content)


def compress_tree(tree, title):
    extra_tree = deepcopy(tree)
    min_characters_to_consider = 300
    max_words_per_slide = 140

    for section in tree:
        if section == 'About the ' + title:
            continue
        new = ''
        for sub_section in tree[section]:
            if len(tree[section][sub_section]) < min_characters_to_consider:
                del extra_tree[section][sub_section]
                continue
            try:
                old = new
                new = sub_section
                if len(tree[section][old].split(' ')) + len(tree[section][new].split(' ')) < max_words_per_slide:
                    extra_tree[section][f'{old} and {new}'] = extra_tree[section][old] + \
                        ' ' + extra_tree[section][new]
                    del extra_tree[section][old]
                    del extra_tree[section][new]
            except Exception:
                pass
    return extra_tree


def remove_useless_paragraphs(tree):
    useless_paragraph_titles = ['External links', 'References', 'See also', 'Further reading', 'Explanatory notes', 'Citations', 'Notes',
                                'In popular culture', 'Bibliography', 'Footnotes', 'Defined', 'Selected bibliography', 'Still need help?',
                                'Public sculptures', 'Gallery', 'Sources', 'Sources cited', 'Works cited', 'Academic research',
                                'Conferences', 'Journals', 'Additional images', 'Reviews', 'General sources', 'Notes and references',
                                'General references', 'General bibliography', 'Appearances in contemporary culture', 'Cited sources',
                                'Popular culture', 'Related reading', 'Library Support']

    for paragraph_title in useless_paragraph_titles:
        try:
            del tree[paragraph_title]
        except Exception:
            pass

    return tree


def clean_text(text):
    text = re_sub('\n+', ' ', text)
    text = re_sub(' ?\(.*\)', '', text)
    text = text.replace('  ', ' ')

    return text

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

def calculate_rouge(reference, hypothesis):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return scores

if __name__ == '__main__':
    wikipedia_topics = [
    # "Universe",
    "Olympics",
    # "Jazz"
    ]
    language = 'en'

    with open('./summarizations.txt', 'r') as f:
        my_summary = f.readlines()

    for i, title in enumerate(wikipedia_topics):
        url, summary, sections, title = find_url(title, language)

        tree = create_content_tree(summary, sections, title)

        final_text  = sum_sequential(tree, 100, 120)
        rouge_scores = calculate_rouge(my_summary[i], json.dumps(final_text))
        print(f"ROUGE scores for {title}:")
        print(f"ROUGE-1: {rouge_scores['rouge1']}")
        print(f"ROUGE-2: {rouge_scores['rouge2']}")
        print(f"ROUGE-L: {rouge_scores['rougeL']}")