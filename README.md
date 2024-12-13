**Overview**
Our project goal is to provide an app that users can search for items from both Target and Whole Foods and use different functions of the app to compare and contrast the prices of different items. 

This project works by scraping data from Target and Whole Foods using Selenium, then using that data to create an interactive app using Dash. Finally, the app is hosted on render at https://pic-16b-group-2-project.onrender.com/. 

-Using Selenium to scrape: Both websites were scraped using Selenium. Then, the data was cleaned and stored in a combined csv file. 
-Dash: We used dash to create a simple app that takes in the csv file and presents it in an easy to read format for the user.
-Render: We used Render to host our app on a site that can be easily accessed from a link. 

1. The dash website should first make the consumer choose a category among Fresh Produce, Meat & Seafood, Snacks, Beverages, Breakfast & Cereal, Bakery, Dairy & Eggs, and Frozen. 
2. After choosing the category, the consumer searches for the product they are trying to purchase. Then the dash website should return a list of products in order of low Price/Quantity of both Target and wholefoods separately. 
3. The list of products is from everything in "Name" column that contains the keyword that consumer searched for. For instance, if the consumer searched for "watermelon" the website's list should have "Fresh Cut Watermelon". 
4. The consumer repeats searching for the products they want to purchase, and the price gets accumulated. 
5. The website finally compares the total price of the two groceries, in the case of purchasing the products in that combination the consumer chose. 

***Thus this interactive website will then visualize the price data, enabling users to easily compare items and make cost-effective shopping decisions.***

# **INSTRUCTIONS**
If you clone our repo, you can put it directly into Render. Here is a tutorial on how to use render. https://github.com/thusharabandara/dash-app-render-deployment

Otherwise, you can use our data file "data_16" and feed it into our dash app code at "dash_final". This will run our app with our data. If you'd like to scrape different data or toggle what links the scraper sifts through, you can look at the "webscraping" folder that has our scraping + data cleaning code. Thanks for reading!
