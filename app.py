from flask import Flask, render_template, request
import pandas as pd
import requests
import plotly.express as px
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API Keys from .env
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def fetch_data():
    url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_API_KEY}&limit=100"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame(columns=["Airline", "Route", "Status"])

    flight_list = []
    for flight in data.get('data', []):
        try:
            airline = flight['airline']['name']
            departure = flight['departure']['airport']
            arrival = flight['arrival']['airport']
            route = f"{departure} → {arrival}"
            status = flight.get('flight_status') or "Unknown"
            flight_list.append([airline, route, status])
        except Exception:
            continue

    return pd.DataFrame(flight_list, columns=["Airline", "Route", "Status"])

def load_mock_pricing_data():
    try:
        df = pd.read_csv("pricing_data.csv", parse_dates=["Date"])
        return df
    except Exception as e:
        print(f"Error loading pricing data: {e}")
        return pd.DataFrame(columns=["Route", "Date", "Price"])

def get_price_trend_for_route(route, df_pricing):
    df_route = df_pricing[df_pricing["Route"] == route]
    if df_route.empty:
        return None
    fig = px.line(df_route, x="Date", y="Price", title=f"Price Trend for {route}")
    fig.update_layout(autosize=True, margin=dict(l=40, r=40, t=40, b=40))
    return fig

def generate_gpt_summary(df):
    if df.empty:
        return "No data available to summarize."

    summary = f"""
    Top Airlines: {df['Airline'].value_counts().head(3).to_dict()}.
    Top Routes: {df['Route'].value_counts().head(3).to_dict()}.
    Flight Status Counts: {df['Status'].value_counts().to_dict()}.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional data analyst."},
                {"role": "user", "content": f"Please summarize this airline market data in simple terms: {summary}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT Error: {e}")
        return "Could not generate GPT summary."

@app.route('/', methods=['GET'])
def index():
    df = fetch_data()
    pricing_df = load_mock_pricing_data()

    routes = sorted(df['Route'].dropna().unique())
    statuses = sorted(df['Status'].dropna().unique())

    selected_route = request.args.get('route', '')
    selected_status = request.args.get('status', '')

    if selected_route:
        df = df[df['Route'] == selected_route]
    if selected_status:
        df = df[df['Status'] == selected_status]

    # Visuals
    top_airlines = df['Airline'].value_counts().head(5).reset_index()
    top_airlines.columns = ['Airline', 'Count']
    fig1 = px.bar(top_airlines, x='Airline', y='Count', title="Top 5 Airlines")

    status_count = df['Status'].value_counts().reset_index()
    status_count.columns = ['Status', 'Count']
    fig2 = px.pie(status_count, names='Status', values='Count', title="Flight Status Distribution")

    top_routes = df['Route'].value_counts().head(5).reset_index()
    top_routes.columns = ['Route', 'Count']
    fig3 = px.bar(top_routes, x='Route', y='Count', title="Top 5 Popular Routes")

    # Price trend
    price_plot = None
    if selected_route:
        fig_price = get_price_trend_for_route(selected_route, pricing_df)
        if fig_price:
            price_plot = fig_price.to_html(full_html=False)

    # GPT Insight
    gpt_summary = generate_gpt_summary(df)

    return render_template(
        'index.html',
        plot1=fig1.to_html(full_html=False),
        plot2=fig2.to_html(full_html=False),
        plot3=fig3.to_html(full_html=False),
        price_plot=price_plot,
        gpt_summary=gpt_summary,
        routes=routes,
        statuses=statuses,
        selected_route=selected_route,
        selected_status=selected_status
    )

if __name__ == '__main__':
    app.run(debug=True)
