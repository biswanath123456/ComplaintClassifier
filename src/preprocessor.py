import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

STOP_WORDS = set(stopwords.words("english"))    # Use a set for faster lookups
KEEP_WORDS = {"not", "no", "never", "without", "neither", "nor", "down", "slow", "wrong", "broken", "blocked", "failed", "missing"} #Negations and some words that can indicate negative sentiment or issues
STOP_WORDS -= KEEP_WORDS   #Remove negations from stop words

lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.lower()     #Convert to lowercase
    text = re.sub(r"http\S+|www\S+", "", text) ##Remove URLs
    text = re.sub(r"\S+@\S+", "", text)     ##Remove email addresses
    text = re.sub(r"\d+", " num ", text)    ##Replace numbers with a placeholder
    text = text.translate(str.maketrans("", "", string.punctuation))    ##Remove punctuation

    tokens = text.split()   
    tokens = [
        lemmatizer.lemmatize(t)
        for t in tokens
        if t not in STOP_WORDS and len(t) > 1
    ]   #Lemmatize and remove stop words and single-character tokens

    return " ".join(tokens)