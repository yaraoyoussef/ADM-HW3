'''
Functions to get regions, coordinates of the restaurants, and plot them on a map in a proper way
'''
# importing all necessary libraries 
from bs4 import BeautifulSoup

# Function to extract the region name of a restaurant 
def get_region_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    region = ''

    # Finding the correct div where 'region' is 
    breadcrumb = soup.find("div", class_="wrap-breadcrumb")
    if breadcrumb:
        breadcrumb_links = breadcrumb.find_all("a")
        if len(breadcrumb_links) > 2:
            region = breadcrumb_links[2].get_text(strip=True)

    return region

# Function to obtain coordinates by geopy
def get_coordinates(city,region,geolocator):
    
    # Combining city and region in order to find the coordinates
    location_query = f"{city}, {region}"
    
    try:
        location = geolocator.geocode(location_query, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None  
    except Exception as e:
        print(f"Error with {city}, {region} - {e}")
        return None, None
    

# Find the stored coordinates for the city of the row  
def apply_coordinates(row,city_coords):
    city_key = f"{row['city']}, {row['region']}"
    return city_coords.get(city_key, (None, None))


# Function to assign color based on price
def price_to_color(price):
    if price.count('€') == 4:
        return 'red'
    elif price.count('€') == 3:
        return 'orange'
    elif  price.count('€') == 2:
        return 'green'
    else:
        return 'blue'
    
