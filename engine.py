'''
Search engine module
'''

'''
First we are going to create a conjunctive search engine
Goal is to return restaurnants where query terms appear in the description
'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
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

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_vector = tfidf_vectorizer.fit_transform(df_restaurants['cleaned_desc'])

    tfidf_df = pd.DataFrame(tfidf_vector.toarray(), index=df_restaurants['restaurantName'], columns=tfidf_vectorizer.get_feature_names_out())

    tfidf_df = tfidf_df.stack().reset_index()
    tfidf_df.columns = ['restaurantName', 'term', 'tfidf_value']

    for index, row in tfidf_df.iterrows():
        if row['tfidf_value'] > 0:
            if row['term'] in inverted_index.keys():
                inverted_index[row['term']].append((row['restaurantName'], row['tfidf_value']))
            else:
                inverted_index[row['term']] = [(row['restaurantName'], row['tfidf_value'])]


    with open('ranked_search_inverted_index.json', 'w') as output:
        json.dump(inverted_index, output, indent=4, sort_keys=False)

def process_query(query):

    with open('ranked_search_inverted_index.json', 'r') as infile:
        words_dict = json.load(infile)

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_vector = tfidf_vectorizer.fit_transform([query])

    query_terms = tfidf_vectorizer.get_feature_names_out()

    doc_scores = {}
    for word in query_terms:
        if word in words_dict:
            for res_name, tfidf_score in words_dict[word]:
                if res_name not in doc_scores:
                    doc_scores[res_name] = []
                doc_scores[res_name].append((word, tfidf_score))

    results = []

    for restaurant, words in doc_scores.items():
        res_vec = np.zeros(len(query_terms))
        for word, score in words:
            idx = np.where(query_terms == word)[0][0]
            res_vec[idx] = score
        
        similarity = cosine_similarity(tfidf_vector, res_vec.reshape(1,-1))[0][0]

        results.append((restaurant, similarity))
    
    results.sort(key=lambda x: x[1], reverse=True)

    return results
    