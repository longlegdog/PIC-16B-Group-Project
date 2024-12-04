#!/usr/bin/env python
# coding: utf-8

# In[27]:


import dash
from dash import dcc, html, Input, Output, State, ctx, ALL
import pandas as pd
import plotly.express as px

#load csv file
data_file = r'data_16b.csv'
df = pd.read_csv(data_file)

#clean the data, handle inconsistencies with pricing
def clean_price(row):
    price = row["Price"]
    if isinstance(price, str):
        if "/" in price:  #handle $3.00/lb cases
            price = price.split("/")[0].strip()  #extract numeric part
        price = price.replace("$", "").strip()  #remove dollar sign
    try:
        return float(price)
    except ValueError:
        return None  

df["Price"] = df.apply(clean_price, axis=1)

#initialize
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server=app.server
app.title = "Grocery Price Comparison"

#add "All" as an option
category_options = [{"label": "All", "value": "All"}] + [
    {"label": cat, "value": cat} for cat in df["Category"].unique()
]

#app layout
app.layout = html.Div([
    html.H1("Grocery Price Comparison", style={'text-align': 'center'}),
    
    html.Div([  #dropdown for category selection
        html.Label("Choose a Category:"),
        dcc.Dropdown(
            id="category-dropdown",
            options=category_options,
            placeholder="Select a category"
        ),
    ], style={'margin-bottom': '20px'}),
    
    html.Div([  #search functionality
        html.Label("Search for a Product:"),
        dcc.Input(id="product-search", type="text", placeholder="Enter product name..."),
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
    ]),
])

#store baskets for Target and Whole Foods
baskets = {"Target": [], "Whole Foods": []}
pagination = {"Target": 5, "Whole Foods": 5}

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

    #update Target basket
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
    Output("funnel-chart", "figure"),
    Input("store-dropdown", "value")
)
def update_funnel_chart(selected_store):
    #filter data based on the selected store
    if selected_store == "All":
        filtered_data = df.groupby(["Category", "Store"]).size().reset_index(name="Count")
    else:
        filtered_data = df[df["Store"] == selected_store].groupby(["Category"]).size().reset_index(name="Count")

    #sort categories by most to least items
    filtered_data = filtered_data.sort_values("Count", ascending=False)

    #create the funnel chart
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

if __name__ == "__main__":
    app.run_server(debug=True, port=8099)


# In[ ]:




