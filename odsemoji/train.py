X = reacts['text'].fillna("_na_").values
y = reacts[ktop_cols].fillna(0).values
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1)



#Load pikled data
#train_test_split
#tokenize, get word_index
#prepare embedding
#
if __name__ == '__main__':
    train()
