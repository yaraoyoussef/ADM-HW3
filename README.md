# ADM-HW3
# Project Overview

This project was developed as a solution to the third homework of the ADM course. It focuses on analyzing and processing data related to restaurants, leveraging various datasets, modules, and tools.

---

## Project Structure

### **1. Files and Folders**
- **`files_tsv/`**  
  Contains TSV files for each restaurant, providing basic information about each one.

- **`restaurants_html/`**  
  Contains the saved pages of the website. Each subfolder within holds the HTML content of the respective restaurant listed on the page.

- **`MyFunctions/`**  
  Includes all the modules and functions used throughout the project. These are imported into the main code for execution.

---

### **2. Key Files**

- **`inverted_index.json`**  
  A file that maps each cleaned word from restaurant descriptions to its corresponding `term_id` and a list of restaurants where the word appears.

- **`ranked_search_inverted_index.json`**  
  Contains a mapping of `term_id` to a list of lists in the format `[restaurantName, tf-idf score]`. This allows ranking based on the term's importance in restaurant descriptions.

- **`restaurant_urls.txt`**  
  A file containing all the restaurant URLs that were parsed for their HTML content at the start of the project.

- **`vocabulary.csv`**  
  Maps each `term_id` to the corresponding cleaned word that appears in the restaurant descriptions.

---

### **3. Main Code**

- **`main.ipynb`**  
  The main notebook of the project, which integrates all parts of the analysis. It includes step-by-step explanations and the corresponding outputs.

---

## How to Use

1. **Explore the data**  
   - Refer to the `files_tsv/` folder for individual restaurant information.  
   - Use `restaurants_html/` for HTML content and `df_restaurants_coordinates.csv` for geolocation data.  

2. **Understand preprocessing and functionality**  
   - Review the `MyFunctions/` folder for reusable modules and functions.  
   - Examine the `inverted_index.json` and `ranked_search_inverted_index.json` files for insights into text processing and ranking.

3. **Reproduce results**  
   - Open and run the `main.ipynb` notebook to follow the workflow and reproduce results.

---

# Datasets

- **'df_restaurants'** 
| A dataset created wih the basic information extracted for each restaurant

- **`df_restaurants_coordinates.csv`**  
  A dataset containing all restaurants, their information, and their respective coordinates.

- **`gi_comuni.xlsx`**  
  A dataset used to retrieve the coordinates of various Italian comunes. Downloaded from https://www.gardainformatica.it/database-comuni-italiani, that gets the informations from reliable sources, such as ISTAT.

---

## Notes

- Ensure the required libraries and dependencies are installed before running the code.  
- Use the provided datasets carefully, as they are integral to the analysis pipeline.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

