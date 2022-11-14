# NOTE: This script contains relative paths that point to files outside of this directory (because they
# are too large to fit). It is included in this repository purely for clarity.

import pandas as pd
import numpy as np
import json

print("Reading in all tweets...")
tweets = pd.read_csv("./Twitter/all_tweets.tsv", sep='\t', usecols=['text'])

# Take random sample of 1,000,000 tweets
tweets = tweets.sample(n=50000)

# Sanity check: how many tweets are in the set?
print(len(tweets['text']))

from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from typing import List
import string
import re

class TweetPreprocessor():
    """
    Tweet Preprocessor

    Accepts tweets and runs preprocessing on them to produce BOW models and vocabularies
    """
    vocab: dict
    bow: np.ndarray
    processed_tweets: List[str]
    
    def preprocess(self, twitter_corpus: List[str]):
        """
        Preprocess Twitter corpus
        
        Parameters
        ----------
        twitter_corpus: list of twitter strings
        """

        tknzr = TweetTokenizer(preserve_case=False, reduce_len=True)
        lmtzr = WordNetLemmatizer()
        vctrzr = CountVectorizer()
        stop_words = set(stopwords.words('english'))

        # Remove links from tweets
        corpus_nolinks = [re.sub(r"http\S+", "", twt) for twt in twitter_corpus]

        # Run tweets through NLTK's TweetTokenizer
        tweets_tknzd = [tknzr.tokenize(twt) for twt in corpus_nolinks]

        # Remove stopwords and punctuation
        tweets_tokens = [[word for word in twt if not (word in stop_words) and not (word in string.punctuation)] for twt in tweets_tknzd]

        # Lemmatize tokens and join with spaces
        tweets_processed = [" ".join([lmtzr.lemmatize(word) for word in twt]) for twt in tweets_tokens]

        # Form BOW model
        X = vctrzr.fit_transform(tweets_processed)
        bow = X.toarray()
        vocab = vctrzr.get_feature_names_out()

        # Define class attributes
        self.vocab = {word: index for index, word in enumerate(vocab)}
        self.bow = bow
        self.processed_tweets = tweets_processed

    def get_vocab(self):
        """
        Return the vocabulary of the Twitter corpus

        Returns
        -------
        dict: Keys as words and values as the index of the word in the vocabulary
        """
        return self.vocab

    def get_bow(self):
        """
        Return the Bag of Words (BOW) model of the Twitter corpus

        Returns
        -------
        ndarray: Matrix of rows as documents (tweets) and columns as words (from the vocabulary)
        """
        return self.bow

    def get_processed_tweets(self):
        """
        Return the processed tweets

        Returns
        -------
        List[str]: List of lemmatized tweets
        """
        return self.processed_tweets



# Initialize preprocessor
print("Initializing preprocessor...")
preprocessor = TweetPreprocessor()

# Preprocess training and testing sets
print("Preprocessing tweets...")
preprocessor.preprocess(tweets['text'])

# Delete tweets dataframe to free up memory
del tweets

# Get processed tweets
print("Saving processed tweets...")
tweets_processed = preprocessor.get_processed_tweets()

# Save processed tweets
with open("./Twitter/all_tweets_data/processed_tweets.txt", 'w') as file:
    for twt in tweets_processed:
        file.write(twt + '\n')

# Get vocabulary
print("Saving vocabulary...")
vocab = preprocessor.get_vocab()

# Save vocabulary
with open("./Twitter/all_tweets_data/tweets_vocab.json", 'w') as vocab_file:
    json.dump(vocab, vocab_file, indent=3)

# Get Bag of Words model for training set
print("Saving bag-of-words")
bow = preprocessor.get_bow()
del preprocessor
np.savetxt("./Twitter/all_tweets_data/bow.csv", bow, delimiter=',', fmt='%s')