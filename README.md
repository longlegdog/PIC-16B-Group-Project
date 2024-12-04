Our project goal is to provide an app that users can search for items from both Target and Whole Foods and use different functions of the app to compare and contrast the prices of different items. 

This project works by scraping data from Target and Whole Foods using Selenium, then using that data to create an interactive app using Dash. Finally, the app is hosted on render at https://pic-16b-group-2-project.onrender.com/. 

-Using Selenium to scrape: Both websites were scraped using Selenium. Then, the data was cleaned and stored in a combined csv file. 
-Dash: We used dash to create a simple app that takes in the csv file and presents it in an easy to read format for the user.
-Render: We used Render to host our app on a site that can be easily accessed from a link. 
** For anyone to use this code, you only need data_16b.csv and dash_new.ipynb to run the Dash app. If you want to rescrape, you can look into our progress code and rescrape. However, this will take potentially 1 hour or more. If you have a render account, you can go to render.com and pass this repository to make a new web service. 

1. The dash website should first make the consumer choose a category among Fresh Produce, Meat & Seafood, Snacks, Beverages, Breakfast & Cereal, Bakery, Dairy & Eggs, and Frozen. 
2. After choosing the category, the consumer searches for the product they are trying to purchase. Then the dash website should return a list of products in order of low Price/Quantity of both Target and wholefoods separately. 
3. The list of products is from everything in "Name" column that contains the keyword that consumer searched for. For instance, if the consumer searched for "watermelon" the website's list should have "Fresh Cut Watermelon". 
4. The consumer repeats searching for the products they want to purchase, and the price gets accumulated. 
5. The website finally compares the total price of the two groceries, in the case of purchasing the products in that combination the consumer chose. 

***Thus this interactive website will then visualize the price data, enabling users to easily compare items and make cost-effective shopping decisions.
