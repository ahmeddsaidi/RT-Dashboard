import requests
from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092', 
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

API_KEY = '1VDL9ZMWAIJ3S78P'
SYMBOL = 'IBM'
API_URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={SYMBOL}&interval=5min&apikey={API_KEY}"

while True:
    try:
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()

            time_series = data.get("Time Series (5min)", {})

            if time_series:
                for timestamp, values in time_series.items():
                    stock_data = {
                        "timestamp": timestamp,
                        "open": values.get("1. open"),
                        "high": values.get("2. high"),
                        "low": values.get("3. low"),
                        "close": values.get("4. close"),
                        "volume": values.get("5. volume")
                    }

                    producer.send('stock-topic', stock_data)
                    producer.flush()
                    print(f"Sent: {stock_data}")
            else:
                print("No time series data found.")

        else:
            print(f"Error fetching data: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    time.sleep(1.5) 