import pandas as pd
from pathlib import Path
from odsemoji.tokenization import text2tagged


#X = reacts['text'].fillna("_na_").values
#y = reacts[ktop_cols].fillna(0).values
#X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1)



#Load pickled data

#train_test_split

#Filter :tada:, urls

#tokenize, get word_index
#prepare embedding
#
if __name__ == '__main__':
    BASE_DIR = Path("../input/export_Feb_8_2018")
    file_cache = Path("../input/all_threads.pkl.compress")

    channels = ['_jobs', 'career']

    if not file_cache.exists():
        print("No data")
        exit(1)
    df = pd.read_pickle(str(file_cache), compression="gzip")
    df = df[:10]
    print(text2tagged(df["text"]))
