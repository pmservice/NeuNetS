import re


def pad_and_str2idx(str2idx, max_length, words):
    '''
    Converts words to indices
    pads the sentence to the max sentence length with PAD token
    '''
    if len(words) > max_length:
        words = words[:max_length]
    mapped_array = list(map(lambda x:str2idx.get(x, str2idx['UNK']), words))
    if len(words) < max_length:
        pad_idx = str2idx['PAD']
        mapped_array.extend([pad_idx for i in range(max_length - len(words))])
    return mapped_array

def regex_replace(trans_dict):
    '''
    create a regex for the words to be replacedx
    '''
    rx = re.compile('|'.join(map(re.escape,trans_dict)))
    def find(match):
        return trans_dict[match.group(0)]
    def replace(text):
        return rx.sub(find, text)
    return replace

def create_trans_dict():
    '''
    create a dictionary with which tokens must be replaced to which
    '''
    ms_word_punc_map = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201C": "\"",
        "\u201D": "\""
    }
    spaced_out = {"n't": " n't ", "'ve": " 've ", "'ll": " 'll ", "'re": " 're ",
                       "'s": " 's ", "'m": " 'm ", "'d": " 'd ", ';': ' ; ', '"': ' " ',
                       ',': ' , ', '.': ' . ', '/': ' / ', '?': ' ? ', '!': ' ! '}
    control_chars = {chr(i) : None for i in list(range(0, 32)) + list(range(127, 160)) }
    trans_dict = {**ms_word_punc_map, **spaced_out, **control_chars, "\\s+": " "}
    return trans_dict

def tokenize(text):
    '''
     Remove unnecessary spaces and replace special characters
    '''
    trans_dict = create_trans_dict()
    translate = regex_replace(trans_dict)
    text = text.strip().lower()
    text = translate(text)
    return text
