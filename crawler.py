'''
Creating the web crawler in order to extract all the restaurants from the Michelin Guide Website
'''
import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup

def link_finder(URL):
    # Define headers to make the request look like it's coming from a regular browser.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # List to store the links 
    urls=[]
    # Iterate on each page and saving its content into the html_content variable
    for page in range(1,101):
        # get url of each page
        url = URL + f'page/{page}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html_content = response.text
        else:
            print("Error during download of current page:", response.status_code)

        # Pase the content of each page
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all the links in the page 
        restaurant_links = soup.find_all("a", class_="link")
        url_base="https://guide.michelin.com"
        page_urls = []
        # Iterate through all links and extract the URL of each link and concatenate it with the base url
        for i in restaurant_links:
            href = i.get("href")
            href= url_base + href
            page_urls.append(href)
        urls.append(page_urls)
    urls = [url for page_urls in urls for url in page_urls]
    print(urls)

    # Only keep the restaurants links and make sure there are no duplicates
    rest_urls = []
    for url in urls:
        if '/restaurant/' in url and url not in rest_urls:
            rest_urls.append(url)

    # Save all links of restaurants in a file
    with open("restaurant_urls.txt", "w") as file:
        for url in rest_urls:
            file.write(url + "\n")

def webpage_downloader():
    # Iterate through links of restaurants
    with open("restaurant_urls.txt", "r") as file:
        urls = file.read().splitlines()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Main folder where to download HTML of each restaurant on each page
    main_folder = "restaurants_html"
    Path(main_folder).mkdir(exist_ok=True)

    # Number of the pages
    page_number = 1

    # Number of restaurants in current page
    restaurant_count = 0
    restaurants_per_page = 20 

    for url in urls:
        # Define folder for each page
        page_folder = os.path.join(main_folder, f"page_{page_number}")
        Path(page_folder).mkdir(exist_ok=True)

        try:
            # Download the HTML of each restaurant
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Name of the restaurant
                filename = url.split("/")[-1] + ".html"
                filepath = os.path.join(page_folder, filename)

                # Save the HTML
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(response.text)

                print(f"Successfully downloaded: {filename} in {page_folder}")

            else:
                print(f"Error {response.status_code} per URL: {url}")
                break

            restaurant_count += 1
            if restaurant_count % restaurants_per_page == 0:
                page_number += 1

        except Exception as e:
            print(f"Error during download of {url}: {str(e)}")

    print("Download completed successfully")

def begin():
    FIRST_URL = "https://guide.michelin.com/en/it/restaurants/"

    link_finder(FIRST_URL)
    webpage_downloader()