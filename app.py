#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go


# In[11]:


import dash
from dash import dcc, html, Input, Output, State, ctx
import pandas as pd
import plotly.graph_objects as go

# Load the CSV file
data_file = r'data_16b.csv'

df = pd.read_csv(data_file)

#preprocess to clean data
def clean_price(row):
    price = row["Price"]
    if isinstance(price, str):
        if "/" in price:  #handle $3.00/lb cases
            price = price.split("/")[0].strip()  #extract numeric part
        price = price.replace("$", "").strip()  #remove dollar sign
    try:
        return float(price)
    except ValueError:
        return None  #handle invalid prices gracefully

df["Price"] = df.apply(clean_price, axis=1)

#initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server= app.server
app.title = "Grocery Price Comparison"

#add "All" to the dropdown options
category_options = [{"label": "All", "value": "All"}] + [
    {"label": cat, "value": cat} for cat in df["Category"].unique()
]

#define the layout
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
        html.Button("More from Target", id="more-target-button", n_clicks=0, style={'display': 'none'}),
        html.Button("More from Whole Foods", id="more-wholefoods-button", n_clicks=0, style={'display': 'none'}),
    ]),

    dcc.Graph(id="price-bar-graph"),
])

#initialize store limits
store_limits = {"Target": 5, "Whole Foods": 5}

#callback to search and display products
@app.callback(
    [Output("product-results", "children"),
     Output("more-target-button", "style"),
     Output("more-wholefoods-button", "style"),
     Output("price-bar-graph", "figure")],
    [Input("search-button", "n_clicks"),
     Input("more-target-button", "n_clicks"),
     Input("more-wholefoods-button", "n_clicks")],
    [State("category-dropdown", "value"),
     State("product-search", "value")],
    prevent_initial_call=True
)
def search_products(search_clicks, more_target_clicks, more_wholefoods_clicks, category, product_name):
    #determine which button was clicked
    triggered_id = ctx.triggered_id
    
    #reset store limits and graph on search
    if triggered_id == "search-button":
        store_limits["Target"] = 5
        store_limits["Whole Foods"] = 5
    
    #increment store limits on "More" button clicks
    if triggered_id == "more-target-button":
        store_limits["Target"] += 5
    elif triggered_id == "more-wholefoods-button":
        store_limits["Whole Foods"] += 5
    
    #validate inputs
    if not product_name:
        return "Please enter a product name.", {"display": "none"}, {"display": "none"}, go.Figure()
    
    #filter data based on category and product name
    if category == "All" or category is None:
        filtered_df = df[df["Name"].str.contains(product_name, case=False, na=False)]
    else:
        filtered_df = df[(df["Category"] == category) & (df["Name"].str.contains(product_name, case=False, na=False))]
    
    if filtered_df.empty:
        return "No products found.", {"display": "none"}, {"display": "none"}, go.Figure()
    
    #ensure valid prices
    filtered_df = filtered_df.dropna(subset=["Price"])
    
    #sort by price
    sorted_target = filtered_df[filtered_df["Store"] == "Target"].sort_values("Price")
    sorted_wholefoods = filtered_df[filtered_df["Store"] == "Whole Foods"].sort_values("Price")
    
    #limit the number of displayed items
    limited_target = sorted_target.head(store_limits["Target"])
    limited_wholefoods = sorted_wholefoods.head(store_limits["Whole Foods"])
    
    #generate results
    target_list = html.Div([
        html.H3("Target:"),
        html.Ul([html.Li(f"{row['Name']} - ${row['Price']:.2f} per unit") for _, row in limited_target.iterrows()]),
    ], style={'margin-bottom': '20px'})

    wholefoods_list = html.Div([
        html.H3("Whole Foods:"),
        html.Ul([html.Li(f"{row['Name']} - ${row['Price']:.2f} per unit") for _, row in limited_wholefoods.iterrows()]),
    ], style={'margin-bottom': '20px'})
    
    #determine button visibility
    target_button_style = {"display": "block"} if len(sorted_target) > store_limits["Target"] else {"display": "none"}
    wholefoods_button_style = {"display": "block"} if len(sorted_wholefoods) > store_limits["Whole Foods"] else {"display": "none"}
    
    #create grouped bar chart
    fig = go.Figure()
    if not limited_target.empty:
        fig.add_trace(go.Bar(
            x=list(range(len(limited_target))),
            y=limited_target["Price"],
            name="Target",
            marker_color="#8B0000",
            hovertext=limited_target.apply(
                lambda row: f"{row['Name']} (${row['Price']:.2f})", axis=1
            ),
            hoverinfo="text+y"
        ))
    if not limited_wholefoods.empty:
        fig.add_trace(go.Bar(
            x=list(range(len(limited_target), len(limited_target) + len(limited_wholefoods))),
            y=limited_wholefoods["Price"],
            name="Whole Foods",
            marker_color="#BAFFC9",
            hovertext=limited_wholefoods.apply(
                lambda row: f"{row['Name']} (${row['Price']:.2f})", axis=1
            ),
            hoverinfo="text+y"
        ))

    fig.update_layout(
        title="Price Comparison Between Stores",
        xaxis_title="Product Index",
        yaxis_title="Price ($)",
        barmode="group",
        legend_title="Store"
    )
    
    return html.Div([target_list, wholefoods_list]), target_button_style, wholefoods_button_style, fig

#run the app
if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




