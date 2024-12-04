#!/usr/bin/env python
# coding: utf-8

# In[12]:


import dash
from dash import dcc, html, Input, Output, State, ctx, ALL
import pandas as pd


# Load the CSV file
data_file = r'data_16b.csv'
df = pd.read_csv(data_file)

# Preprocess to clean data
def clean_price(row):
    price = row["Price"]
    if isinstance(price, str):
        if "/" in price:  # Handle $3.00/lb cases
            price = price.split("/")[0].strip()  # Extract numeric part
        price = price.replace("$", "").strip()  # Remove dollar sign
    try:
        return float(price)
    except ValueError:
        return None  # Handle invalid prices gracefully

df["Price"] = df.apply(clean_price, axis=1)

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Grocery Price Comparison"

# Add "All" to the dropdown options
category_options = [{"label": "All", "value": "All"}] + [
    {"label": cat, "value": cat} for cat in df["Category"].unique()
]

# Define the layout
app.layout = html.Div([
    html.H1("Grocery Price Comparison", style={'text-align': 'center'}),
    
    html.Div([
        html.Label("Choose a Category:"),
        dcc.Dropdown(
            id="category-dropdown",
            options=category_options,
            placeholder="Select a category"
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([
        html.Label("Search for a Product:"),
        dcc.Input(id="product-search", type="text", placeholder="Enter product name..."),
        html.Button("Search", id="search-button", n_clicks=0),
    ], style={'margin-bottom': '20px'}),
    
    html.Div(id="product-results", style={'margin-bottom': '20px'}),

    html.Div([
        html.H3("Selected Products:", style={'text-align': 'center'}),
        
        html.Div([
            html.H4("Target:", style={'margin-top': '10px'}),
            html.Div(id="basket-target", style={'margin-bottom': '10px'}),
            html.H4("Total for Target: $", id="total-target", style={'margin-bottom': '10px'}),
        ], style={'border': '1px solid #8B0000', 'padding': '10px', 'margin-bottom': '20px'}),

        html.Div([
            html.H4("Whole Foods:", style={'margin-top': '10px'}),
            html.Div(id="basket-wholefoods", style={'margin-bottom': '20px'}),
            html.H4("Total for Whole Foods: $", id="total-wholefoods"),
        ], style={'border': '1px solid #BAFFC9', 'padding': '10px'}),

        # Clear Selection Button
        html.Button("Clear Selection", id="clear-selection-button", n_clicks=0, 
                    style={'margin-top': '20px', 'background-color': '#f44336', 'color': 'white'}),
    ], style={'text-align': 'center'}),
])


# Store baskets for Target and Whole Foods
baskets = {"Target": [], "Whole Foods": []}
pagination = {"Target": 5, "Whole Foods": 5}

@app.callback(
    Output("product-results", "children"),
    [Input("search-button", "n_clicks"),
     Input({"type": "see-more", "store": ALL}, "n_clicks")],
    [State("category-dropdown", "value"),
     State("product-search", "value")]
)
def search_products(search_clicks, see_more_clicks, category, product_name):
    triggered_id = ctx.triggered_id

    global pagination

    # Reset pagination when the search button is clicked
    if triggered_id == "search-button":
        pagination = {"Target": 5, "Whole Foods": 5}

    # Filter data based on category and product name
    if not product_name:
        return "Please enter a product name."

    if category == "All" or category is None:
        filtered_df = df[df["Name"].str.contains(product_name, case=False, na=False)]
    else:
        filtered_df = df[(df["Category"] == category) & (df["Name"].str.contains(product_name, case=False, na=False))]

    if filtered_df.empty:
        return "No products found."

    # Ensure valid prices
    filtered_df = filtered_df.dropna(subset=["Price"])

    # Sort by lowest price
    filtered_df = filtered_df.sort_values(by="Price")

    # Adjust pagination based on "See More" button clicks
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "see-more":
        store = triggered_id["store"]
        pagination[store] += 5

    def create_product_list(products, store):
        product_items = [
            html.Li(html.Button(f"{row['Name']} - ${row['Price']:.2f}",
                                id={"store": store, "name": row["Name"]}))
            for _, row in products.iterrows()
        ]
        visible_items = product_items[:pagination[store]]
        see_more_button = html.Button(f"See More for {store}", id={"type": "see-more", "store": store}) \
            if len(product_items) > pagination[store] else None
        return html.Div([html.Ul(visible_items), see_more_button])

    target_products = filtered_df[filtered_df["Store"] == "Target"]
    wholefoods_products = filtered_df[filtered_df["Store"] == "Whole Foods"]

    return html.Div([
        html.Div([
            html.H3("Target:"),
            create_product_list(target_products, "Target"),
        ]),
        html.Div([
            html.H3("Whole Foods:"),
            create_product_list(wholefoods_products, "Whole Foods"),
        ])
    ])

@app.callback(
    [Output("basket-target", "children"),
     Output("basket-wholefoods", "children"),
     Output("total-target", "children"),
     Output("total-wholefoods", "children")],
    [Input({"store": "Target", "name": ALL}, "n_clicks"),
     Input({"store": "Whole Foods", "name": ALL}, "n_clicks")],
    [State({"store": "Target", "name": ALL}, "id"),
     State({"store": "Whole Foods", "name": ALL}, "id")]
)
def update_baskets(target_clicks, wholefoods_clicks, target_ids, wholefoods_ids):
    global baskets

    # Update Target basket
    for click, product_id in zip(target_clicks, target_ids):
        if click and not any(item["name"] == product_id["name"] for item in baskets["Target"]):
            product_name = product_id["name"]
            product_row = df[df["Name"] == product_name]
            if not product_row.empty:
                price = product_row.iloc[0]["Price"]
                baskets["Target"].append({"name": product_name, "price": price})

    # Update Whole Foods basket
    for click, product_id in zip(wholefoods_clicks, wholefoods_ids):
        if click and not any(item["name"] == product_id["name"] for item in baskets["Whole Foods"]):
            product_name = product_id["name"]
            product_row = df[df["Name"] == product_name]
            if not product_row.empty:
                price = product_row.iloc[0]["Price"]
                baskets["Whole Foods"].append({"name": product_name, "price": price})

    # Generate output
    target_items = [f"{item['name']} - ${item['price']:.2f}" for item in baskets["Target"]]
    wholefoods_items = [f"{item['name']} - ${item['price']:.2f}" for item in baskets["Whole Foods"]]

    target_total = sum(item["price"] for item in baskets["Target"])
    wholefoods_total = sum(item["price"] for item in baskets["Whole Foods"])

    return (
        html.Ul([html.Li(item) for item in target_items]),
        html.Ul([html.Li(item) for item in wholefoods_items]),
        f"Total for Target: ${target_total:.2f}",
        f"Total for Whole Foods: ${wholefoods_total:.2f}"
    )
    

@app.callback(
    [Output("basket-target", "children", allow_duplicate=True),
     Output("basket-wholefoods", "children", allow_duplicate=True),
     Output("total-target", "children", allow_duplicate=True),
     Output("total-wholefoods", "children", allow_duplicate=True)],
    Input("clear-selection-button", "n_clicks"),
    prevent_initial_call=True
)
def clear_selections(clear_clicks):
    global baskets
    baskets = {"Target": [], "Whole Foods": []}
    return (
        html.Ul([]),
        html.Ul([]),
        "Total for Target: $0.00",
        "Total for Whole Foods: $0.00"
    )


if __name__ == "__main__":
    app.run_server(debug=True)


# In[ ]:




