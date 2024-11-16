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
import pandas as pd

import MyFunctions.engine as engine

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

def find_restaurants(query, df):
    query = clean_desc(query)

    intersection_set = engine.conjunctive_query(query)

    found_rest = []

    found_rest = pd.DataFrame(found_rest)

    for restaurant in intersection_set:
        filtered_df = df.query("restaurantName == @restaurant")
        found_rest = pd.concat([found_rest, filtered_df])

    found_rest.reset_index(drop=True, inplace=True)
    found_rest = found_rest.filter(items=['restaurantName', 'address', 'description', 'website'])
    found_rest = found_rest.rename(columns={'restaurantName':'Restaurant Name', 'address':'Address', 'description': 'Description', 'website':'Website'})


    return found_rest

def find_ranked_restaurants(query, k, df_restaurants):
    ranked_result = engine.process_query(clean_desc(query), df_restaurants)
    df_restaurants['similarity'] = 0
    ranked_df = []
    ranked_df = pd.DataFrame(ranked_df)
    for restaurant in ranked_result[:k]:
        filtered_df = df_restaurants.loc[df_restaurants['restaurantName'] == restaurant[0]]
        filtered_df['similarity'] = restaurant[1]
        ranked_df = pd.concat([ranked_df, filtered_df])

    ranked_df = ranked_df.filter(items=['restaurantName', 'address', 'description', 'website','similarity'])

    pd.set_option('display.max_colwidth', None)
    return ranked_df