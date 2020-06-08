import argparse
import nltk
import pyphen


# parse input data
def parse_arguments():
    """

    :return: Text to be edited
    """
    parser = argparse.ArgumentParser(
        description="Input text to be edited"
    )

    parser.add_argument(
        "text",
        metavar="input text",
        type=str
    )

    args = parser.parse_args()
    return args.text


# clean input data
def clean_input(text):
    """
    Remove non-ASCII characters
    :param text: User input
    :return: cleaned text
    """
    return str(text.encode().decode("ascii", errors="ignore"))


# tokenization
def preprocess_input(text):
    """
    Tokenizer
    :param text: cleaned text
    :return: tokenized text
    """
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sentence) for sentence in sentences]
    return tokens


def count_word_usage(tokens, word_list):
    """
    Count occurrences of list of words
    :param tokens: list of tokens
    :param word_list: list of words
    :return: number of times words appear in input list
    """
    return len([word for word in tokens if word.lower() in word_list])


def compute_average_word_length(tokens):
    """
    calculate average word length for a sentence
    :param tokens: list of words
    :return: average length of words in input list
    """
    lengths = [len(word) for word in tokens]
    return sum(lengths) / len(lengths)


def compute_total_average_word_length(sentence_list):
    """
    calculate average word length for sentences
    :param sentence_list: list of sentences, each sentence is list of words
    :return: average length of words in the input list
    """
    lengths = [compute_average_word_length(tokens) for tokens in sentence_list]
    return sum(lengths) / len(lengths)


def compute_total_unique_words_fraction(sentence_list):
    """
    compute fraction of unique words
    :param sentence_list: list of sentences, each sentence is list of words
    :return: fraction of unique words in input list
    """
    words = [word for word_list in sentence_list for word in word_list]
    unique_words = set(words)
    return len(unique_words) / len(words)


def count_word_syllables(word):
    """
    count syllables in a word
    :param word: one word string
    :return: number of syllables
    """
    # returns the input word with hyphens inserted between each syllable
    hyph_dict = pyphen.Pyphen(lang="en_US")
    hyphenated = hyph_dict.inserted(word)
    return len(hyphenated.split("-"))


def count_sentence_syllables(tokens):
    """
    count syllables in sentence
    :param tokens: list of words
    :return: number of syllables in input sentence
    """

    # filter punctuation because our tokenizer tokenizes punctuation as separate words
    punctuation = ".,!?/"
    return sum([count_word_syllables(word) for word in tokens if word not in punctuation])


def count_total_syllables(sentence_list):
    """
    count syllables in list of sentences
    :param sentence_list: list of sentences, each sentence is list of words
    :return: number of syllables in sentences
    """
    return sum([count_sentence_syllables(sentence) for sentence in sentence_list])


def count_words_per_sentence(tokens):
    """
    count words in a sentence
    :param tokens: list of words
    :return: number of words in a sentence
    """
    punctuation = ".,!?/"
    return len([word for word in tokens if word not in punctuation])


def count_total_words(sentence_list):
    """
    count total words in list of sentences
    :param sentence_list: list of sentences, each sentence is list of words
    :return: number of words in input list
    """
    return sum([count_words_per_sentence(sentence) for sentence in sentence_list])


def compute_flesch_reading_ease(num_syllables, num_words, num_sentences):
    """
    computes readability score from summary statistics,
    based on https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease
    :param num_syllables: number of syllables
    :param num_words: number of words
    :param num_sentences: number of sentences
    :return: readability score
    """
    return (
            206.85
            - 1.015 * (num_words / num_sentences)
            - 84.6 * (num_syllables / num_words)
    )


def get_reading_level_from_flesch(flesch_score):
    """
    calculate reading level from flesch score,
    based on Thresholds taken from https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
    :param flesch_score:
    :return: reading level
    """
    if flesch_score < 30:
        return "Very difficult to read"
    elif flesch_score < 50:
        return "Difficult to read"
    elif flesch_score < 60:
        return "Fairly difficult to read"
    elif flesch_score < 70:
        return "Plain English"
    elif flesch_score < 80:
        return "Fairly easy to read"
    elif flesch_score < 90:
        return "Easy to read"
    else:
        return "Very easy to read"


# generate features
def get_suggestions(sentence_list):
    """
    compute frequency of few common verbs and connectors,
    count adverb usage,
    determine the Flesch readability score
    :param sentence_list: list of sentences, each sentence is list of words
    :return: suggestions to improve input
    """
    # usage of words like "told", "said" etc
    told_said_usage = sum(count_word_usage(tokens, ["told", "said"])
                          for tokens in sentence_list)

    but_and_usage = sum(count_word_usage(tokens, ["but", "and"])
                        for tokens in sentence_list)

    # adverbs starting with "wh" usage
    wh_adverbs = ["when", "where", "why", "whence", "whereby", "whereupon"]
    wh_adverb_usage = sum(count_word_usage(tokens, wh_adverbs)
                          for tokens in sentence_list)

    adverb_usage = f"Adverb usage: {told_said_usage} told/said," \
                   f" {but_and_usage} but/and," \
                   f" {wh_adverb_usage} wh adverbs"

    # word lengths
    average_word_length = compute_total_average_word_length(sentence_list)

    # fraction of unique words
    unique_word_fraction = compute_total_unique_words_fraction(sentence_list)

    word_stats = f"Average word length {average_word_length:.2f}," \
                 f" fraction of unique words {unique_word_fraction:.2f}"

    # summary statistics
    num_syllables = count_total_syllables(sentence_list)
    num_words = count_total_words(sentence_list)
    num_sentences = len(sentence_list)

    syllables_count = f"{num_syllables} syllables," \
                      f" {num_words} words," \
                      f" {num_sentences} sentences"

    # flesch reading score
    flesch_score = compute_flesch_reading_ease(num_syllables,
                                               num_words,
                                               num_sentences)
    reading_level = get_reading_level_from_flesch(flesch_score)

    flesch = f"{num_syllables} syllables," \
             f" {flesch_score:.2f} flesh_score," \
             f" reading level: {reading_level} "

    result_str = adverb_usage + "\n" + word_stats + "\n" + syllables_count + "\n" + flesch

    return result_str


if __name__ == "__main__":
    input_text = parse_arguments()
    processed = clean_input(input_text)
    tokenized_sentences = preprocess_input(processed)
    suggestions = get_suggestions(tokenized_sentences)
    print(suggestions)

    # sample input/output
    '''
    "Is this workflow any good?"
    Adverb usage: 0 told/said, 0 but/and, 0 wh adverbs
    Average word length 3.67, fraction of unique words 1.00
    6 syllables, 5 words, 1 sentences
    6 syllables, 100.26 flesh_score, reading level: Very easy to read
    '''
