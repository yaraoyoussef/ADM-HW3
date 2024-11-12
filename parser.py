'''
Module to parse all the webpages downloaded by the crawler
'''

import os
from bs4 import BeautifulSoup
import re

def extract_restaurant_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Estrarre il nome del ristorante
    restaurant_name = soup.find("h1", class_="data-sheet__title").get_text(strip=True) if soup.find("h1", class_="data-sheet__title") else ''

    # Finding Address and Pricing
    big_div = soup.find_all("div", class_="data-sheet__block--text")
    if big_div:
        address_city__postal_country, price_range = big_div[0], big_div[1]
        address_city__postal_country_text = " ".join(address_city__postal_country.stripped_strings)
        address_city__postal_country_list = re.split(r',\s*', address_city__postal_country_text)

        country = address_city__postal_country_list[-1]
        postal = address_city__postal_country_list[-2]
        city = address_city__postal_country_list[-3]
        address = ', '.join(address_city__postal_country_list[:-3])

        #Price 
        if big_div[1]:
            price_range = price_range.get_text(strip=True)
            price_range_list=price_range.split('·')

            price = price_range_list[0]
            price = re.sub(r"\s+", "", price)

            # Cuisine type
            cuisine_type = price_range_list[1]
            cuisine_type = re.sub(r"\s+", "", cuisine_type)

    # description 
    description = soup.find("div", class_="data-sheet__description").get_text(strip=True) if soup.find("div", class_="data-sheet__description") else ''

    # facilities

    services_column = soup.find('div', class_='col col-12 col-lg-6')
    facilities_services = [item.get_text(strip=True) for item in services_column.find_all('li') ] if services_column else []

    #CreditCards

    creditCards_column = soup.find('div',class_='list--card')
    if creditCards_column:
        creditCards_img =[img['data-src'] for img in creditCards_column.find_all('img')]
        creditCards_names = [re.search(r'icons/([a-zA-Z]+)', cc).group(1).capitalize() for cc in creditCards_img]
    else: 
        creditCards_names = []

    # Phone Number
    phone_number = soup.find('span', class_="flex-fill").get_text(strip=True) if soup.find("span", class_="flex-fill") else ''

    # Website
    link_div = soup.find('div', class_='collapse__block-item link-item')

    if link_div:
        website_tag = link_div.find('a', class_='link js-dtm-link')
        website = website_tag['href'] if website_tag else ''
    else:
        website = ''




    restaurant_info = {
        "restaurantName": restaurant_name,
        "address": address,
        "city": city,
        "postalCode": postal,
        "country": country,
        "priceRange": price,
        "cuisineType": cuisine_type,
        "description": description,
        "facilitiesServices": facilities_services,
        "creditCards": creditCards_names,
        "phoneNumber": phone_number,
        "website": website
    }
    return restaurant_info