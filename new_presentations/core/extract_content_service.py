from re import sub as re_sub, split as re_split
from copy import deepcopy


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
