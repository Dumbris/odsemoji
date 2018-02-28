import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from odsemoji.tokenization import text2tagged
from odsemoji.preprocessing import TextsToSequences, Padder



DEBUG = True
ktop_cols = ['reaction_+1', 'reaction_heavy_plus_sign', 'reaction_joy',
               'reaction_fire', 'reaction_notbad', 'reaction_trollface',
               'reaction_100', 'reaction_povar', 'reaction_muscle',
               'reaction_true-story', 'reaction_yeah-sure', 'reaction_ban',
               'reaction_facepalm', 'reaction_slava', 'reaction_putin',
               'reaction_be-a-man', 'reaction_but_why', 'reaction_kekeke',
               'reaction_wat', 'reaction_ternaus']

#Load pickled data
def load_threads(file_cache: Path):
    if not file_cache.exists():
        print("No data")
        exit(1)
    df = pd.read_pickle(str(file_cache), compression="gzip")
    if DEBUG:
        df = df[:10]
    return df




#
if __name__ == '__main__':
    BASE_DIR = Path("../input/export_Feb_8_2018")
    file_cache = Path("../input/all_threads.pkl.compress")
    reacts = load_threads(file_cache)

    #train_test_split
    X = reacts['text'].fillna("_na_").values
    y = reacts[ktop_cols].fillna(0).values
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1)

    #TODO: Filter :tada:, urls

    #tokenize, get word_index
    X_train_tokenized = text2tagged(X_train["text"])
    sequencer = TextsToSequences(num_words=max_features)
    padder = Padder(maxlen)

    print("Start fitting sequenser")
    sequencer.fit_on_texts(np.hstack([list_sentences_train, list_sentences_test]))
    len(sequencer.word_index)

    #prepare embedding
