from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objs as go
import plotly
import json
import openai
from datetime import datetime
import re

app = Flask(__name__)

# Set your OpenAI API key here or environment variable OPENAI_API_KEY
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Utility function: get sample airline booking-related data by scraping a public source or using free API
def fetch_airline_data():
    """
    Scrape or get open sample airline fare & route data.
    Since real booking data is paywalled, will scrape airline route prices example from a "fake" or demo source.

    We'll scrape sample data from a public free flights route ranking page:
    https://www.kayak.com/flights/AUS-BNE/2023-10-01 (example)

    For demonstration, scrape route, prices, dates from a demo web page with sample routes and prices.
    """

    # Kayak is dynamic and uses JS, so scraping static HTML won't fetch prices. 
    # We'll provide fallback sample data for demonstration:

    sample_data = [
        {"route": "Sydney (SYD) - Brisbane (BNE)", "date": "2023-10-01", "price": 120},
        {"route": "Melbourne (MEL) - Sydney (SYD)", "date": "2023-10-02", "price": 110},
        {"route": "Brisbane (BNE) - Perth (PER)", "date": "2023-10-03", "price": 250},
        {"route": "Sydney (SYD) - Melbourne (MEL)", "date": "2023-10-01", "price": 115},
        {"route": "Adelaide (ADL) - Sydney (SYD)", "date": "2023-10-02", "price": 180},
        {"route": "Gold Coast (OOL) - Melbourne (MEL)", "date": "2023-10-03", "price": 220},
        {"route": "Perth (PER) - Brisbane (BNE)", "date": "2023-10-04", "price": 260},
        {"route": "Sydney (SYD) - Gold Coast (OOL)", "date": "2023-10-05", "price": 130},
        {"route": "Melbourne (MEL) - Perth (PER)", "date": "2023-10-01", "price": 240},
        {"route": "Brisbane (BNE) - Adelaide (ADL)", "date": "2023-10-04", "price": 230},
    ]

    return pd.DataFrame(sample_data), None


def process_data(df):
    """
    Clean and process data:
    - Extract origin and destination from 'route'
    - Convert date to datetime
    - Aggregate to find popular routes, average prices, demand by date
    """

    # Extract origin and destination
    def extract_airports(route):
        m = re.match(r'([a-zA-Z\s]+) \((\w{3})\) - ([a-zA-Z\s]+) \((\w{3})\)', route)
        if m:
            return m.group(1).strip(), m.group(3).strip()
        return None, None

    df[['origin', 'destination']] = df['route'].apply(lambda x: pd.Series(extract_airports(x)))

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Add demand column sample (simulate demand by estimate inverse of price scaled):
    max_price = df['price'].max()
    df['demand_estimate'] = ((max_price - df['price']) / max_price * 100).astype(int) + 20  # base+20

    return df


def generate_insights(df):
    """
    Generate textual insights using OpenAI API based on processed data.
    """

    popular_routes = df.groupby('route').agg({'demand_estimate': 'mean', 'price': 'mean'}).sort_values(by='demand_estimate', ascending=False).head(3)
    popular_routes_list = popular_routes.reset_index().to_dict(orient='records')

    price_trend = df.groupby('date').agg({'price': 'mean'}).reset_index()
    high_demand_dates = df.groupby('date').agg({'demand_estimate': 'mean'}).sort_values(by='demand_estimate', ascending=False).head(3).reset_index()

    prompt = f"""
    You are a helpful data analyst assistant specialized in airline market demand.

    Given the following data summaries:

    Popular Routes by Demand and Average Price:
    {popular_routes_list}

    Average Price Per Date:
    {price_trend.to_dict(orient='records')}

    High Demand Dates:
    {high_demand_dates.to_dict(orient='records')}

    Please provide a concise summary of demand trends, pricing changes, and recommend any valuable insights for airline market demand optimization.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert data analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        insight_text = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        insight_text = f"Error generating insights: {str(e)}"

    return insight_text


def create_charts(df):
    """
    Create interactive Plotly charts for:
    - Popular Routes by Demand
    - Price Trends over Dates
    """

    df_route = df.groupby('route').agg({'demand_estimate': 'mean'}).sort_values('demand_estimate', ascending=False).reset_index()

    fig_routes = go.Figure(
        data=[
            go.Bar(
                x=df_route['route'],
                y=df_route['demand_estimate'],
                marker_color='indianred'
            )
        ],
        layout=go.Layout(
            title="Average Demand by Route",
            xaxis_title="Route",
            yaxis_title="Average Demand Estimate",
            margin=dict(l=40, r=20, t=60, b=120),
        )
    )

    routesJSON = json.dumps(fig_routes, cls=plotly.utils.PlotlyJSONEncoder)

    df_date = df.groupby('date').agg({'price': 'mean'}).reset_index()

    fig_price = go.Figure(
        data=[
            go.Scatter(
                x=df_date['date'],
                y=df_date['price'],
                mode='lines+markers',
                marker_color='blue'
            )
        ],
        layout=go.Layout(
            title="Average Price Trend Over Dates",
            xaxis_title="Date",
            yaxis_title="Average Price (AUD)",
            margin=dict(l=40, r=20, t=60, b=40),
        )
    )

    priceJSON = json.dumps(fig_price, cls=plotly.utils.PlotlyJSONEncoder)

    return routesJSON, priceJSON


@app.route("/", methods=['GET', 'POST'])
def index():
    error = None
    df = None
    insights = ""
    routes_chart = ""
    price_chart = ""

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        origin_filter = request.form.get('origin').strip() if request.form.get('origin') else ""
        destination_filter = request.form.get('destination').strip() if request.form.get('destination') else ""

        df_raw, error = fetch_airline_data()
        if error:
            return render_template('index.html', error=error)

        df = process_data(df_raw)

        if start_date_str:
            try:
                start_date = pd.to_datetime(start_date_str)
                df = df[df['date'] >= start_date]
            except:
                error = "Invalid start date format. Use YYYY-MM-DD."

        if end_date_str:
            try:
                end_date = pd.to_datetime(end_date_str)
                df = df[df['date'] <= end_date]
            except:
                error = "Invalid end date format. Use YYYY-MM-DD."

        if origin_filter:
            df = df[df['origin'].str.contains(origin_filter, case=False, na=False)]

        if destination_filter:
            df = df[df['destination'].str.contains(destination_filter, case=False, na=False)]

        if df.empty:
            error = "No data found for the selected filters."
        else:
            insights = generate_insights(df)
            routes_chart, price_chart = create_charts(df)

    return render_template(
        'index.html', 
        error=error,
        insights=insights,
        routes_chart=routes_chart,
        price_chart=price_chart,
        filters={
            'start_date': request.form.get('start_date', ''),
            'end_date': request.form.get('end_date', ''),
            'origin': request.form.get('origin', ''),
            'destination': request.form.get('destination', '')
        }
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)