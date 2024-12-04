#!/usr/bin/env python
# coding: utf-8

# In[5]:


import dash
from dash import dcc, html, Input, Output, State, ctx, ALL
import pandas as pd
import plotly.express as px

#read csv file into dataframe
data_file = r'data_16b.csv'
df = pd.read_csv(data_file)

#data should be clean, just double checking here
def clean_price(row):
    price = row["Price"]
    if isinstance(price, str):
        if "/" in price:  #handle $3.00/lb cases
            price = price.split("/")[0].strip()  #extract number
        price = price.replace("$", "").strip()  #remove dollar sign
    try:
        return float(price)
    except ValueError:
        return None  

df["Price"] = df.apply(clean_price, axis=1)

#initialize the app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server=app.server
app.title = "Grocery Price Comparison"

#adding "All" as an option
category_options = [{"label": "All", "value": "All"}] + [
    {"label": cat, "value": cat} for cat in df["Category"].unique()
]

#define the layout
app.layout = html.Div([
    html.H1("Target vs Whole Foods Grocery Price Comparison", style={'text-align': 'center'}),
    
    html.Div([  #dropdown for category selection
        html.Label("Choose a Category:"),
        dcc.Dropdown(
            id="category-dropdown",
            options=category_options,
            placeholder="All"
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([  #search functionality
        html.Label("Search for a Product:"),
        dcc.Input(id="product-search", type="text", placeholder="Enter product name/keyword..."),
        html.Button("Search", id="search-button", n_clicks=0),
    ], style={'margin-bottom': '20px'}),
    
    html.Div(id="product-results", style={'margin-bottom': '20px'}),

    html.Div([  #basket display and totals
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

        #clear Selection Button
        html.Button("Clear Selection", id="clear-selection-button", n_clicks=0, 
                    style={'margin-top': '20px', 'background-color': '#f44336', 'color': 'white'}),
    ], style={'text-align': 'center'}),
    html.Div([  #price range slider
        html.Label("Filter Funnel Chart by Price Range:"),
        dcc.RangeSlider(
            id="price-range-slider",
            min=0,
            max=df["Price"].max(),
            step=0.1,
            value=[0, df["Price"].max()],
            marks={i: f"${i}" for i in range(0, int(df["Price"].max()) + 1, 10)}
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([  #funnel chart visualization
        html.H3("Category Distribution Funnel Chart", style={'text-align': 'center'}),
        dcc.Dropdown(
            id="store-dropdown",
            options=[
                {"label": "All Stores", "value": "All"},
                {"label": "Target", "value": "Target"},
                {"label": "Whole Foods", "value": "Whole Foods"}
            ],
            value="All",  #default selection
            clearable=False,
            style={'width': '50%', 'margin': '0 auto'}
        ),
        dcc.Graph(id="funnel-chart", style={"height": "600px"}),
    ])
])



#store baskets for Target and Whole Foods
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

    #resetting pagination to show only 5 products when search is clicked
    if triggered_id == "search-button":
        pagination = {"Target": 5, "Whole Foods": 5}

    #filter data based on category and product name
    if not product_name:
        return "Please enter a product name."

    if category == "All" or category is None:
        filtered_df = df[df["Name"].str.contains(product_name, case=False, na=False)]
    else:
        filtered_df = df[(df["Category"] == category) & (df["Name"].str.contains(product_name, case=False, na=False))]

    if filtered_df.empty:
        return "No products found."

    #double checking no N/A prices
    filtered_df = filtered_df.dropna(subset=["Price"])

    #sort by lowest price
    filtered_df = filtered_df.sort_values(by="Price")

    #"See More" button shows 5 more at a time
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

    #clicking on a product adds to basket for Target
    for click, product_id in zip(target_clicks, target_ids):
        if click and not any(item["name"] == product_id["name"] for item in baskets["Target"]):
            product_name = product_id["name"]
            product_row = df[df["Name"] == product_name]
            if not product_row.empty:
                price = product_row.iloc[0]["Price"]
                baskets["Target"].append({"name": product_name, "price": price})

    #update Whole Foods basket
    for click, product_id in zip(wholefoods_clicks, wholefoods_ids):
        if click and not any(item["name"] == product_id["name"] for item in baskets["Whole Foods"]):
            product_name = product_id["name"]
            product_row = df[df["Name"] == product_name]
            if not product_row.empty:
                price = product_row.iloc[0]["Price"]
                baskets["Whole Foods"].append({"name": product_name, "price": price})

    #generate output
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
def clear_selections(clear_clicks):#adding button to empty basket
    global baskets
    baskets = {"Target": [], "Whole Foods": []}
    return (
        html.Ul([]),
        html.Ul([]),
        "Total for Target: $0.00",
        "Total for Whole Foods: $0.00"
    )

@app.callback(
    Output("funnel-chart", "figure"),
    [Input("store-dropdown", "value"),
     Input("price-range-slider", "value")]
)
def update_funnel_chart(selected_store, price_range):#funnel chart by category
    filtered_df = df[(df["Price"] >= price_range[0]) & (df["Price"] <= price_range[1])]
    if selected_store == "All":
        filtered_data = filtered_df.groupby(["Category", "Store"]).size().reset_index(name="Count")
    else:
        filtered_data = filtered_df[filtered_df["Store"] == selected_store].groupby(["Category"]).size().reset_index(name="Count")

    filtered_data = filtered_data.sort_values("Count", ascending=False)

    fig = px.funnel(
        filtered_data,
        y="Category",
        x="Count",
        color="Store" if selected_store == "All" else None,
        title=f"Category Distribution - {selected_store}",
        labels={"Count": "Number of Products", "Category": "Product Category"},
    )
    fig.update_layout(height=600)
    return fig

#run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8099)


# In[ ]:




