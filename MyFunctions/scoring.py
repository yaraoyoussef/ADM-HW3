import MyFunctions.utilities as utilities
import heapq

'''
In this file we define the functions used to 
1. Calculate the final score given to a restaurant
2. Rank the restaurants returned by the 2.1 search engine
'''

# Define price range scoring (lower is better)
PRICE_RANGE_SCORES = {
    '€': 1.0,       # Very Affordable
    '€€': 0.8,      # Affordable
    '€€€': 0.5,     # Moderate
    '€€€€': 0.2     # Expensive
}

# Defined function to calculate score of a restaurant
def calc_score(restaurant_name, cosine_similarity, user_preferences, df_restaurants):
    score = 0

    # Description match
    score += 0.25 * cosine_similarity

    # Cuisine match operates counting the number of matching cuisines
    cuisine_types = df_restaurants.loc[df_restaurants['restaurantName'] == restaurant_name, 'cuisineType'].values
    matching_cuisines = set(cuisine_types).intersection(user_preferences['cuisines'])
    if matching_cuisines:
        score += 0.25 * (len(matching_cuisines) / len(user_preferences['cuisines']))
    
    # Facilities and services operates in same way as cuisines
    services = df_restaurants.loc[df_restaurants['restaurantName'] == restaurant_name, 'facilitiesServices'].values
    matching_facilities = set(services[0]).intersection(user_preferences['facilities'])
    if matching_facilities:
        score += 0.25 * (len(matching_facilities) / len(user_preferences['facilities']))
    
    # Price range
    price_range = df_restaurants.loc[df_restaurants['restaurantName'] == restaurant_name, 'priceRange'].values
    price_score = PRICE_RANGE_SCORES.get(price_range[0])
    score += 0.25 * price_score

    return score

# Ranking function using heapq for top-k
def rank_restaurants(user_preferences, top_k, df_restaurants):
    heap = []
    scores = []

    ### Take relevant documents based on normal search engine (of point 2.1)
    restaurants_df = utilities.find_restaurants(user_preferences['query'], df_restaurants)
    # Add the cleaned description column to the dataframe
    restaurants_df['cleaned_desc'] = restaurants_df['description'].apply(utilities.clean_desc)
    # Rank the found restaurants based on their similarity score to the query
    restaurants_df = utilities.find_ranked_restaurants(user_preferences['query'], top_k, restaurants_df)
    for index, restaurant in restaurants_df.iterrows():
        rest_name = restaurant['restaurantName']
        cos_sim = restaurant['similarity']
        # Calculate score
        score = calc_score(rest_name, cos_sim, user_preferences, df_restaurants)
        scores.append(score)
        heapq.heappush(heap, (-score, index))
        if len(heap)> top_k:
            heapq.heappop(heap)

    # Extract sorted restaurants from the heap
    ranked_restaurants = [heapq.heappop(heap) for _ in range(len(heap))]
    ranked_indices = [item[1] for item in ranked_restaurants]
    ranked_scores = [-item[0] for item in ranked_restaurants]

    df_without_last_column = restaurants_df.iloc[:, :-1]

    # Add scores to the original DataFrame
    df_without_last_column['score'] = scores
    #df_without_last_column = df_without_last_column.loc[ranked_indices].reset_index(drop=True)


    # Ensure the 'score' column reflects the scores in the ranked order
    df_without_last_column['score'] = ranked_scores


    return df_without_last_column