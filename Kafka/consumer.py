from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'stock-topic',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest', 
    group_id='stock-consumer-group'
)

for message in consumer:
    try:
        data = message.value
        print(f"Received message: {data}")

    except Exception as e:
        print(f"Error processing message: {e}")