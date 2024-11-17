import math
import json
import numpy as np
import pandas as pd

def vocabulary_creator(description_set, criteria):
    words_to_int = {}

    counter = 0

    # For every word inside the set passed an argument a different integer is assigned, creating the ID
    for word in description_set:
        words_to_int[counter] = word
        counter += 1
    
    # The Word-ID dictionary is then converted to a dataframe and saved inside a .csv file
    vocab = pd.DataFrame(list(words_to_int.items()), columns=['term_id', 'word'])
    vocab.to_csv(f'{criteria}_vocabulary.csv', index=False)

# TO-FIX

def inverted_index_creator(df_restaurants):

    TO_INVERT = ['restaurantName', 'city', 'cuisineType']

    for criteria in TO_INVERT:
        vocabulary_creator(set(word for text in df_restaurants[criteria] for word in text.split()), criteria)
        word_id = pd.read_csv(f'{criteria}_vocabulary.csv')
        word_to_id = dict(zip(word_id.get('word'), word_id.get('term_id')))

        inverted_index = {}
        for index, row in df_restaurants.iterrows():
            term_frequency = {}
            for word in row[criteria].split():
                if word in term_frequency:
                    term_frequency[word] += 1
                else:
                    term_frequency[word] = 1
            for frequency in term_frequency.values(): frequency / len(row[criteria])

            restaurant_number = len(df_restaurants)
            for word, frequency in term_frequency.items():
                idf = math.log(restaurant_number / 1 + df_restaurants[criteria].str.contains(word).sum())
                tfidf_value = frequency * idf

            if word_to_id.get(word) in inverted_index:
                inverted_index[word_to_id.get(word)].append((row['restaurantName'], tfidf_value))
            else:
                inverted_index[word_to_id.get(word)] = [(row['restaurantName'], tfidf_value)]
        
        with open(f'{criteria}_inverted_index.json', 'w') as outfile:
            json.dump(inverted_index, outfile, indent=4, sort_keys=False)