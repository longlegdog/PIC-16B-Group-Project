import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
import time

# Database setup
conn = sqlite3.connect("walmart_grocery.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS groceries (
        id INTEGER PRIMARY KEY,
        category TEXT,
        name TEXT,
        price REAL,
        quantity TEXT
    )
''')
conn.commit()

# URL and Category Mapping
categories = {
    "Fresh Produce": "https://www.walmart.com/search?q=fresh+produce",
    "Meat & Seafood": "https://www.walmart.com/search?q=meat%20and%20seafood",
    "Snacks": "https://www.walmart.com/search?q=snacks",
    "Pantry": "https://www.walmart.com/search?q=pantry%20food&typeahead=pantry",
    "Beverages": "https://www.walmart.com/search?q=beverages",
    "Breakfast & Cereal": "https://www.walmart.com/search?q=Breakfast+%26+Cereal",
    "Bakery": "https://www.walmart.com/search?q=bakery+all",
    "Dairy & Eggs": "https://www.walmart.com/search?q=Dairy%26Eggs",
    "Frozen": "https://www.walmart.com/search?q=frozen%20meals"
}

# Initialize Selenium WebDriver
def get_driver():
    try:
        return webdriver.Chrome()
    except WebDriverException as e:
        print(f"Error initializing WebDriver: {e}")
        return None  # Optionally return None and handle it in the calling function


driver = get_driver()

# Function to scrape data
def scrape_category(category_name, url):
    global driver
    try:
        driver.get(url)
        time.sleep(3)  # Wait for page to load
        
        # Scraping logic
        products = driver.find_elements(By.CSS_SELECTOR, "div.search-result-gridview-item-wrapper")
        data = []
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, "a.product-title-link span").text
                price = product.find_element(By.CSS_SELECTOR, "span.price-characteristic").text
                quantity = product.find_element(By.CSS_SELECTOR, "span.product-quantity").text
                data.append((category_name, name, float(price), quantity))
            except Exception as e:
                print(f"Skipping a product due to error: {e}")
        
        # Save to database
        cursor.executemany("INSERT INTO groceries (category, name, price, quantity) VALUES (?, ?, ?, ?)", data)
        conn.commit()
        
        # Append to CSV
        df = pd.DataFrame(data, columns=["category", "name", "price", "quantity"])
        df.to_csv("walmart_grocery.csv", mode="a", header=False, index=False)
    
    except NoSuchWindowException:
        print("Browser window was closed; restarting driver.")
        driver.quit()
        driver = get_driver()
        scrape_category(category_name, url)  # Retry scraping the category
    
    except WebDriverException as e:
        print(f"WebDriver exception encountered: {e}")
        driver.quit()
        driver = get_driver()

# Loop through categories
for category_name, url in categories.items():
    scrape_category(category_name, url)

# Close resources
driver.quit()
conn.close()

