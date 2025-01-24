# Import packages
from datetime import date
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State
from bs4 import BeautifulSoup
import requests
import pandas as pd
import plotly_express as px  # import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import requests

# Incorporate data
# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='Hotel Data Dashboard', style={'color': 'black', 'fontSize': 25}),
    html.Div([
        "城市: ",
        dcc.Input(id='myinput', value='台南', type='text'),
        '日期: ',
        dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date(2024, 12, 31),
        initial_visible_month=date(2023, 12, 5),
        end_date = date(2023, 12, 1),
        start_date = date(2023, 11, 30)
    ),
    html.Button(children ='搜尋', id='fetch-button', n_clicks=0)]),
    html.Br(),
    dcc.Graph(id='graph')
])

# Add controls to build the interaction
@callback(
    Output(component_id='graph', component_property='figure'),
    Input('fetch-button', 'n_clicks'),
    State(component_id='myinput', component_property='value'),
    State('my-date-picker-range', 'start_date'),
    State('my-date-picker-range', 'end_date')
    
)
def update_graph(Clicks, myinput, start_date, end_date):
    if Clicks is None:
        return Dash.no_update
    
    url = f'https://www.booking.com/searchresults.html?ss={myinput}&checkin={start_date}&checkout={end_date}&group_adults=2&no_rooms=1&group_children=0&lang=zh-tw&soz=1&lang_changed=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }
    list_ = ['', '&offset=25', '&offset=50', '&offset=75', '&offset=100']
    hotels_data = []

    # change the next page
    for page in list_:
        if len(hotels_data) > 99:
            break
        response  = requests.get(url + page, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the hotel elements in the HTML document
        hotels = soup.findAll('div', {'data-testid': 'property-card'})

        # Loop over the hotel elements and extract the desired data
        for hotel in hotels:
            # Extract the hotel name
            name_element = hotel.find('div', {'data-testid': 'title'})
            name = name_element.text.strip()

            # Extract the hotel location
            location_element = hotel.find('span', {'data-testid': 'address'})
            location = location_element.text.strip()

            # Extract the hotel price
            price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
            if price_element:
                price = price_element.text.strip()
            else:
                price = 'N/A'
            
            # Extract the hotel rating
            rating_element = hotel.find('div', {'class': 'a3b8729ab1 d86cee9b25'})
            if rating_element:
                rating = rating_element.text.strip()
            else:
                rating = 'N/A'
            
            # Extract the hotel distance
            distance_element = hotel.find('span', {'data-testid': 'distance'})
            if distance_element:
                distance = distance_element.text.strip()
            else:
                distance = 'N/A'
            #  Extract the hotel comments
            comments_element = hotel.find('div', {'class': 'a3b8729ab1 e6208ee469 cb2cbb3ccb'})
            if comments_element:
                comments = comments_element.text.strip()
            else:
                comments = 'N/A'

            # data cleaning
            check_list = [name, location, price, rating, distance, comments]
            if 'N/A' in check_list or name in [i['name'] for i in hotels_data]:
                continue
            else:
                price = int(''.join(c for c in price if c.isdigit()))
                rating = float(rating)
                distance = float(''.join(c for c in distance if c.isdigit())) / 1000

            # Append hotes_data with info about hotel
            hotels_data.append({
                'name': name,
                'location': location,
                'price': price,
                'rating': rating,
                'distance': distance,
                'comments': comments
            })
            if len(hotels_data) > 99:
                break

    hotels = pd.DataFrame(hotels_data)

    # Step 3: Data Visualization
    fig = px.scatter(
        hotels,  # 数据集
        x="price",  # x轴
        y="distance",  # y轴
        color="rating",  # 指定颜色
        title="Hotel Price and Distance Scatter Plot", # 標題
        hover_name="name",
        hover_data=['price', 'distance', 'rating']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
