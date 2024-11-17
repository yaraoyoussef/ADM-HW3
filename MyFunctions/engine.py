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

def vocabulary_creator(description_set):
    words_to_int = {}

    counter = 0

    # For every word inside the set passed an argument a different integer is assigned, creating the ID
    for word in description_set:
        words_to_int[counter] = word
        counter += 1
    
    # The Word-ID dictionary is then converted to a dataframe and saved inside a .csv file
    vocab = pd.DataFrame(list(words_to_int.items()), columns=['term_id', 'word'])
    vocab.to_csv('vocabulary.csv', index=False)

def inverted_index_creator(df_restaurants):

    inverted_index = {}

    # Loading the vocabulary for the term to id mapping
    all_words = pd.read_csv('vocabulary.csv')
    word_to_id = dict(zip(all_words['word'], all_words['term_id']))

    # For every review inside the dataframe and for every word in the review we get the corresponding term id from the vocabulary
    for row, review in df_restaurants.iterrows():
        for word in review['cleaned_desc'].split():
            term_id = word_to_id.get(word)
            # Chcking if a given id has already been stored inside the dictionary as key
            if term_id in inverted_index:
                # Checking if the restaurant has beel already inserted inside the list
                if review['restaurantName'] not in inverted_index[term_id]:
                    inverted_index[term_id].append(review['restaurantName'])    # Appending the restaurant name which description contains the given word
            else:
                inverted_index[term_id] = [review['restaurantName']]

    # Saving the created dictionary to a file for later use without new computation
    with open('inverted_index.json', 'w') as output:
        json.dump(inverted_index, output, indent=4, sort_keys=False)
    
def conjunctive_query(query):

    inverted_index = {}

    # Loading the term_id to restaurant names index 
    with open('inverted_index.json', 'r') as input_file:
        inverted_index = json.load(input_file)

    # Loading the vocabulary for mapping puropses
    word_id = pd.read_csv('vocabulary.csv')
    word_to_id = dict(zip(word_id['word'], word_id['term_id']))

    to_intersect = [] # List of sets
    # For every word in the user input query the function adds the restaurant names whose description contains the given word inside a list
    for word in query.split():
        try:
            to_intersect.append(set(inverted_index[str(word_to_id.get(word))])) # Added as a set to later perform set intersection
        except KeyError as notFound:
            print(f'word {word} not present in any description')

    ''' After all the restaurants sets have been added to the list, the function performs an intersection, to only keep the restaurant whose
    description contains every word present in the query. The intersection set is later returned'''
    intersection_set = set.intersection(*to_intersect)

    return intersection_set

def inverted_tfidf(df_restaurants):

    ''' Our goal is to first calculate the term frequencies (TF)
    and then the Inverse Document Ferquency
        1 - Term frequency is defined as the number of times a certain word is present inside a given document
        2 - Invese Document Frequency is the result of a math formula --> log (N/{d: d in D and t in d}
    '''

    inverted_index = {}

    # Loading the vocabulary for mapping purposes
    word_id = pd.read_csv('vocabulary.csv')
    word_to_id = dict(zip(word_id['word'], word_id['term_id']))

    '''For every word inside the dataframe, the function checks the frequency of every term inside the description as per TF definition.
    Once the dictionary term:frequency is created, for every term inside of it the IDF is calculated according to the definition. The obtained
    values are mupltiplied in order to get the TF-IDF value, which is saved inside an inverted index as a restaurant, tfidf_value tuple for evey word.
    The so obtained dictionary is saved in a .json file for later use, to avoid multiple computation.'''

    for index, row in df_restaurants.iterrows():
        desc = row['cleaned_desc']
        restaurant = row['restaurantName']

        # For every cleaned restaurant description we calculate the frequency of every term
        total_words = len(desc.split())
        term_frequency = {}
        for term in desc.split():
            if term in term_frequency:
                term_frequency[term] += 1 # If the word is already present as a key, the fraction represting the frequency is added
            else:
                term_frequency[term] = 1 # Key is initialized with the corresponding word frequency
        for frequency in term_frequency.values(): frequency / total_words

        restaurant_number = len(df_restaurants) # Total number of docs in IDF formula
        for term, frequency in term_frequency.items():
            idf = math.log(restaurant_number / (1 + df_restaurants['cleaned_desc'].str.contains(term).sum())) # restaurant_number is N
            tfidf_value = frequency * idf # As per definition

            if word_to_id.get(term) in inverted_index:
                inverted_index[word_to_id.get(term)].append((restaurant, tfidf_value))
            else:
                inverted_index[word_to_id.get(term)] = [(restaurant, tfidf_value)]

    with open('ranked_search_inverted_index.json', 'w') as output:
        json.dump(inverted_index, output, indent=4, sort_keys=False)

def process_query(query, df_restaurants):

    '''
    Our goal is to:
        1 - Create the vectors for what we want to compare and multiply them
        2 - Divide step 1 prooduct for the product of magnitudes
    
    To do this we want to compare the query to every cleaned description inside the dataframe, and for each one returning the similarity score
    '''
    
    # Loading vocabulary and inverted index for query similarity computation

    word_id = pd.read_csv('vocabulary.csv')
    word_to_id = dict(zip(word_id['word'], word_id['term_id']))

    with open('ranked_search_inverted_index.json', 'r') as infile:
        words_dict = json.load(infile)

    cosine_similarity = {}

    # Query TF-IDF is needed, it's calculated as if it is a new description inside the dataframe
    query_tfidf = {}
    query_len = len(query.split())
    for word in query.split():
        if word in query_tfidf:
            query_tfidf[word] += 1/query_len
        else:
            query_tfidf[word] = 1/query_len

    for term, frequency in query_tfidf.items():
        idf = math.log(len(df_restaurants)+1) / (1 + df_restaurants['cleaned_desc'].str.contains(term).sum())
        tfidf_value = frequency * idf
        query_tfidf[term] = tfidf_value

    # Find the TF-IDF vector for the document
    ''' Once the TF-IDF value is calculated for the query, the function needs to compare the query vector with every description vector in 
    order to compute the cosine similarity.
    To build the description vector the previously saved inverted index is used, mapping every word of the description to the corresponfing tfidf_value'''

    for index, row in df_restaurants.iterrows():
        desc = row['cleaned_desc']
        restaurant_name = row['restaurantName']

        desc_tfidf = {}
        for term in set(desc.split()):
            mapped_id = str(word_to_id.get(term))
            if mapped_id in words_dict:
                for restaurant, tfidf in words_dict[mapped_id]:
                    if restaurant == restaurant_name:
                        desc_tfidf[term] = tfidf

        numerator = 0.0
        for word in set(query.split()):
            numerator += desc_tfidf.get(word, 0) * query_tfidf.get(word, 0)
        
        # Sqrt(restaurant description tfidf^2) * Sqrt(query tfidf^2)
        denominator = math.sqrt(sum(tfidf ** 2 for tfidf in desc_tfidf.values())) * math.sqrt(sum(tfidf ** 2 for tfidf in query_tfidf.values()))

        if denominator == 0:
            cosine_similarity[restaurant_name] = 0
        else:
            cosine_similarity[restaurant_name] = numerator / denominator

    sorted_results = sorted(cosine_similarity.items(), key=lambda x:x[1], reverse=True)    
    
    return sorted_results