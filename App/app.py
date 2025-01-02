import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import os
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

historical_data = {'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

def format_currency(value, symbol="$"):
    if isinstance(value, (int, float)):
        return f"{symbol}{value:,.2f}"
    return "N/A"

app.layout = dbc.Container([
    html.H1("Stock Data Dashboard", className="text-center mb-4"),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Open Price"),
            dbc.CardBody(html.H4(id='open-price', className="text-center font-weight-bold"))
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardHeader("High Price"),
            dbc.CardBody(html.H4(id='high-price', className="text-center font-weight-bold"))
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Low Price"),
            dbc.CardBody(html.H4(id='low-price', className="text-center font-weight-bold"))
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Close Price"),
            dbc.CardBody(html.H4(id='close-price', className="text-center font-weight-bold"))
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Volume"),
            dbc.CardBody(html.H4(id='volume', className="text-center font-weight-bold"))
        ]), width=2),
    ], className="mb-4 justify-content-center"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='historical-line-chart'), width=6),
        dbc.Col(dcc.Graph(id='historical-bar-chart'), width=6)
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-chart'), width=6),
        dbc.Col(dcc.Graph(id='pie-chart'), width=6)
    ], className="mb-4"),
    dbc.Row([dcc.Graph(id='candlestick-chart')]),
    dcc.Interval(id='update-interval', interval=1000, n_intervals=0)
], fluid=True)

def read_latest_data():
    csv_dir = './output_csv2'
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    if not csv_files:
        return None
    latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(csv_dir, f)))
    try:
        df = pd.read_csv(os.path.join(csv_dir, latest_file), names=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df.iloc[-1].to_dict()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

@app.callback(
    [Output('open-price', 'children'), Output('high-price', 'children'),
     Output('low-price', 'children'), Output('close-price', 'children'),
     Output('volume', 'children'), Output('historical-line-chart', 'figure'),
     Output('historical-bar-chart', 'figure'), Output('scatter-chart', 'figure'),
     Output('pie-chart', 'figure'), Output('candlestick-chart', 'figure')],
    [Input('update-interval', 'n_intervals')]
)
def update_dashboard(n):
    global historical_data
    latest_data = read_latest_data()

    if latest_data: 
        open_price = latest_data['open']
        high_price = latest_data['high']
        low_price = latest_data['low']
        close_price = latest_data['close']
        volume = latest_data['volume']
        historical_data['open'].append(open_price)
        historical_data['high'].append(high_price)
        historical_data['low'].append(low_price)
        historical_data['close'].append(close_price)
        historical_data['volume'].append(volume)
    else:
        open_price = historical_data['open'][-1] if historical_data['open'] else 0
        high_price = historical_data['high'][-1] if historical_data['high'] else 0
        low_price = historical_data['low'][-1] if historical_data['low'] else 0
        close_price = historical_data['close'][-1] if historical_data['close'] else 0
        volume = historical_data['volume'][-1] if historical_data['volume'] else 0

    line_chart = {
        'data': [
            {'x': list(range(len(historical_data['open']))),
             'y': historical_data['open'],
             'type': 'line', 'name': 'Open Price'},
            {'x': list(range(len(historical_data['high']))),
             'y': historical_data['high'],
             'type': 'line', 'name': 'High Price'},
            {'x': list(range(len(historical_data['low']))),
             'y': historical_data['low'],
             'type': 'line', 'name': 'Low Price'},
            {'x': list(range(len(historical_data['close']))),
             'y': historical_data['close'],
             'type': 'line', 'name': 'Close Price'},
        ],
        'layout': {
            'title': 'Historical Price Trend',
            'xaxis': {'title': 'Time (Intervals)'},
            'yaxis': {'title': 'Price'},
            'template': 'plotly_dark',
        }
    }

    bar_chart = {
        'data': [
            {'x': list(range(len(historical_data['volume']))),
             'y': historical_data['volume'],
             'type': 'bar', 'name': 'Volume', 'opacity': 0.4},
        ],
        'layout': {
            'title': 'Volume Over Time',
            'xaxis': {'title': 'Time (Intervals)'},
            'yaxis': {'title': 'Volume'},
            'template': 'plotly_dark',
        }
    }

    candlestick_chart = {
        'data': [
            go.Candlestick(
                x=list(range(len(historical_data['open']))),
                open=historical_data['open'],
                high=historical_data['high'],
                low=historical_data['low'],
                close=historical_data['close'],
                name='Candlestick'
            )
        ],
        'layout': {
            'title': 'Candlestick Chart',
            'xaxis': {'title': 'Time (Intervals)'},
            'yaxis': {'title': 'Price'},
            'template': 'plotly_dark',
        }
    }

    scatter_chart = {
        'data': [
            go.Scatter(
                x=historical_data['open'],
                y=historical_data['volume'],
                mode='markers',
                name='Open vs Volume'
            ),
        ],
        'layout': {
            'title': 'Scatter Plot: Open vs Volume',
            'xaxis': {'title': 'Open Price'},
            'yaxis': {'title': 'Volume'},
            'template': 'plotly_dark',
        }
    }

    pie_chart = {
        'data': [
            go.Pie(
                labels=['High Price', 'Low Price'],
                values=[high_price, low_price],
                name='Price Proportion'
            )
        ],
        'layout': {
            'title': 'High vs Low Price Proportion',
            'template': 'plotly_dark',
        }
    }

    return (format_currency(open_price), format_currency(high_price),
            format_currency(low_price), format_currency(close_price),
            f"{volume:,}", line_chart, bar_chart, scatter_chart, pie_chart, candlestick_chart)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051)