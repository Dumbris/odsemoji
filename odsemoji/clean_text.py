import re

hashtags_re = re.compile(r"#\w+[\w'-]*\w+")
ellipsis_re = re.compile(r"\.\.+")
repeating_re = re.compile(r"(\w)\1\1+")
number_re = r"(?:[+-]?\$?\d+(?:\.\d+)?(?:[eE]-?\d+)?%?)(?![A-Za-z])"
numbers_re = re.compile(r"{0}(?:\s*/\s*{0})?".format(number_re))  # deals with fractions

def clean_text(rawText):
    return [re.sub(r'https?:\/\/.*\/\w*', 'URL', text) for text in rawText]

# replace characters with >=3 alphabetic repeating
def normalize_repeated(word, normalize=3):
    return repeating_re.sub(r"\1"*normalize, word)


