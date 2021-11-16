from nltk.corpus import words
# import nltk
# nltk.download('words')

WORDS_SET = set(words.words())
def in_english_dictionary(word):
    return word in WORDS_SET

print(in_english_dictionary('april'))
print(in_english_dictionary('April'))
