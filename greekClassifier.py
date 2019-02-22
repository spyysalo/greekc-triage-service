import json
from delft.utilities.Embeddings import Embeddings
from delft.utilities.Utilities import split_data_and_labels
from delft.textClassification.reader import load_texts_and_classes_greekc
import delft.textClassification
from delft.textClassification import Classifier
import argparse
import keras.backend as K
import time
import codecs
import sys
import select

list_classes = [1]


def train(embeddings_name, fold_count): 
    model = Classifier('greekc', "gru", list_classes=list_classes, use_char_feature=True, max_epoch=30, fold_number=fold_count, 
        use_roc_auc=True, embeddings_name=embeddings_name)

    print('loading greekc corpus...')
    xtr, y = load_texts_and_classes_greekc("/home/felipe/Documents/Github/GreekC-Classification/delft_augmented.train")

    if fold_count == 1:
        model.train(xtr, y)
    else:
        model.train_nfold(xtr, y)
    # saving the model
    model.save()


def train_and_eval(embeddings_name, fold_count): 
    model = Classifier('greekc', "gru", list_classes=list_classes, use_char_feature=True, max_epoch=3, fold_number=fold_count, 
        use_roc_auc=True, embeddings_name=embeddings_name)

    print('loading greekc corpus...')
    xtr, y = load_texts_and_classes_greekc("/home/felipe/Documents/Github/GreekC-Classification/delft_augmented.train")

    # segment train and eval sets
    x_train, y_train, x_test, y_test = split_data_and_labels(xtr, y, 0.9)

    if fold_count == 1:
        model.train(x_train, y_train)
    else:
        model.train_nfold(x_train, y_train)
    model.eval(x_test, y_test)

    # saving the model
    model.save()


# classify a list of texts
def classify(texts, output_format):
    # load model
    model = Classifier('greekc', "gru", list_classes=list_classes)
    model.load()
    start_time = time.time()
    result = model.predict(texts, output_format)
    runtime = round(time.time() - start_time, 3)
    if output_format is 'json':
        result["runtime"] = runtime
    else:
        print("runtime: %s seconds " % (runtime))
    return result



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Sentiment classification of citation passages")

    parser.add_argument("action")
    parser.add_argument("--fold-count", type=int, default=1)

    args = parser.parse_args()

    if args.action not in ('train', 'train_eval', 'classify'):
        print('action not specifed, must be one of [train,train_eval,classify]')

    # Change below for the desired pre-trained word embeddings using their descriptions in the file 
    # embedding-registry.json
    # be sure to use here the same name as in the registry ('glove-840B', 'fasttext-crawl', 'word2vec'), 
    # and that the path in the registry to the embedding file is correct on your system
    embeddings_name = "fasttext_300_opt"

    if args.action == 'train':
        if args.fold_count < 1:
            raise ValueError("fold-count should be equal or more than 1")

        train(embeddings_name, args.fold_count)

    if args.action == 'train_eval':
        if args.fold_count < 1:
            raise ValueError("fold-count should be equal or more than 1")

        y_test = train_and_eval(embeddings_name, args.fold_count)    

    if args.action == 'classify':
        stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
        model = Classifier('greekc', "gru", list_classes=list_classes)
        model.load()
        sys.stdout = stdout

    while 1:
        line = sys.stdin.readline()
        if line:
            result = model.predict([line.strip()], 'json')
            print(json.dumps(result, sort_keys=False, indent=4, ensure_ascii=False))
        else: # an empty line means stdin has been closed
            print('eof')
            exit(0)

    # See https://github.com/tensorflow/tensorflow/issues/3388
    K.clear_session()
