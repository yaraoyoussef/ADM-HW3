'''
Search engine module
'''

'''
First we are going to create a conjunctive search engine
Goal is to return restaurnants where query terms appear in the description
'''
import math
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import json

# Creating the index

def vocabulary_creator(description_set):
    words_to_int = {}

    counter = 0

    for word in description_set:
        words_to_int[counter] = word
        counter += 1
    
    vocab = pd.DataFrame(list(words_to_int.items()), columns=['term_id', 'word'])
    vocab.to_csv('vocabulary.csv', index=False)

def inverted_index_creator(df_restaurants):

    inverted_index = {}

    all_words = set(pd.read_csv('vocabulary.csv'))

    for row, review in df_restaurants.iterrows():
        for word in review['cleaned_desc'].split():
            if word in inverted_index:
                if review['restaurantName'] not in inverted_index[word]:
                    inverted_index[word].append(review['restaurantName'])
            else:
                inverted_index[word] = [review['restaurantName']]

    with open('inverted_index.json', 'w') as output:
        json.dump(inverted_index, output, indent=4, sort_keys=False)
    
def conjunctive_query(query):

    inverted_index = {}
    with open('inverted_index.json', 'r') as input_file:
        inverted_index = json.load(input_file)

    to_intersect = []
    for word in query.split():
        try:
            to_intersect.append(set(inverted_index[word]))
        except KeyError as notFound:
            print(f'word {word} not present in any description')

    intersection_set = set.intersection(*to_intersect)

    return intersection_set

def inverted_tfidf(df_restaurants):

    inverted_index = {}

    # Calculate TF-IDF without using TfifVectorizer

    ''' Our goal is to first calculate the term frequencies (TF)
    and then the Inverse Document Ferquency
        1 - Term frequency is defined as the number of times a certain word is present inside a given document
        2 - Invese Document Frequency is the result of a math formula --> log (N/{d: d in D and t in d}
    '''

    for index, row in df_restaurants.iterrows():
        desc = row['cleaned_desc']
        restaurant = row['restaurantName']

        # For every cleaned restaurant description we calculate the frequency of every term
        total_words = len(desc.split())
        term_frequency = {}
        for term in desc.split():
            if term in term_frequency:
                term_frequency[term] += 1/total_words
            else:
                term_frequency[term] = 1/total_words

        restaurant_number = len(df_restaurants) # Total number of docs in IDF formula
        for term, frequency in term_frequency.items():
            idf = math.log(restaurant_number / (1 + df_restaurants['cleaned_desc'].str.contains(term).sum())) # restaurant_number is N
            tfidf_value = frequency * idf # As per definition

            if term in inverted_index:
                inverted_index[term].append((restaurant, tfidf_value))
            else:
                inverted_index[term] = [(restaurant, tfidf_value)]

    with open('ranked_search_inverted_index.json', 'w') as output:
        json.dump(inverted_index, output, indent=4, sort_keys=False)

def process_query(query, df_restaurants):

    print('Reloaded')
    with open('ranked_search_inverted_index.json', 'r') as infile:
        words_dict = json.load(infile)

    # Calculate the cosine similarity without using external libraries

    '''
    Our goal is to:
        1 - Create the vectors for what we want to compare and multiply them
        2 - Divide step 1 prooduct for the product of magnitudes
    
    To do this we want to compare the query to every cleaned description inside the dataframe, and for each one returning the similarity score
    '''
    cosine_similarity = {}

    # Query TF-IDF is needed
    query_tfidf = {}
    for word in query.split():
        if word in query_tfidf:
            query_tfidf[word] += 1/len(query.split())
        else:
            query_tfidf[word] = 1/len(query.split())

    for term, frequency in query_tfidf.items():
        idf = math.log(len(df_restaurants)+1) / (1 + df_restaurants['cleaned_desc'].str.contains(term).sum())
        tfidf_value = frequency * idf
        query_tfidf[term] = tfidf_value

    # Find the TF-IDF vector for the document

    for index, row in df_restaurants.iterrows():
        desc = row['cleaned_desc']
        restaurant_name = row['restaurantName']

        desc_tfidf = {}
        for term in set(desc.split()):
            if term in words_dict:
                for restaurant, tfidf in words_dict[term]:
                    if restaurant == restaurant_name:
                        desc_tfidf[term] = tfidf

        numerator = 0.0
        for word in set(query.split()):
            numerator += desc_tfidf.get(word, 0) * query_tfidf.get(word, 0)
        
        denominator = math.sqrt(sum(tfidf ** 2 for tfidf in desc_tfidf.values())) * math.sqrt(sum(tfidf ** 2 for tfidf in query_tfidf.values()))

        if denominator == 0:
            cosine_similarity[restaurant_name] = 0
        else:
            cosine_similarity[restaurant_name] = numerator / denominator

    sorted_results = sorted(cosine_similarity.items(), key=lambda x:x[1], reverse=True)    
    
    return sorted_results
