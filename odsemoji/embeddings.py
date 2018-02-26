from gensim.models import fasttext

model = fasttext.FastText.load('/media/data/word2vec/araneum_fasttext/araneum_none_fasttextskipgram_300_5_2018.model')

print(model.most_similar('tensorflow'))
for n in model.most_similar(positive=[u'пожар_NOUN']):
    print(n[0], n[1])


'сепулька' in model.wv.vocab

model['сепулька']

def prepare_embeddings(word_indexes):

    def load_w2v():
        _fname = os.path.join(DATA_DIR, EMBEDDING_FILE)
        w2v_model = models.KeyedVectors.load_word2vec_format(_fname, binary=False)
        return w2v_model

    embeddings = load_w2v()
    # prepare embedding matrix
    nb_words = min(MAX_NB_WORDS, len(word_indexes))
    prepared_embedding_matrix = np.zeros((nb_words, EMBEDDING_DIM))
    for word, n in word_indexes.items():
        if n >= MAX_NB_WORDS:
            continue
        try:
            embedding_vector = embeddings.word_vec(word)
            prepared_embedding_matrix[n] = embedding_vector
        except:
            continue

    return prepared_embedding_matrix
