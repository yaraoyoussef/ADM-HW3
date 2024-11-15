'''
Cleaning and preparing text of description column in df
'''
# Importing all necessary libraries
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from nltk.stem import PorterStemmer

# Function to remove stopwords, punctuation and apply stemming on text  
def clean_desc(desc):
    # Get english stopwords
    stop_words = set(stopwords.words('english'))

    # Applying other necessary cleaning: 1 - lower casing
    desc = desc.lower()

    # Applying other necessary cleaning: 2 - removing special characters, non-alphanumerics 
    desc = re.sub(r'http\S+|www\S+|https\S+', '', desc)  # Remove URLs
    desc = re.sub(r'\S+@\S+', '', desc)  # Remove email addresses
    desc = re.sub(r'[^A-Za-z0-9\s]', '', desc)  # Remove non-alphanumeric characters

    words = word_tokenize(desc)

    stemmer = PorterStemmer()

    remaining = [
        stemmer.stem(word) # Apply stemming at last / same order provided in HW requirements
        for word in words
        if word.lower() not in stop_words and word not in string.punctuation]
    
    # Applying other necessary cleaning: 3 - removing extra spaces 
    cleaned_text = ' '.join(remaining) 
    remaining = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text