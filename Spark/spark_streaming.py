from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType

schema = StructType([
    StructField("timestamp", StringType(), True), 
    StructField("open", FloatType(), True), 
    StructField("high", FloatType(), True), 
    StructField("low", FloatType(), True),   
    StructField("close", FloatType(), True),   
    StructField("volume", IntegerType(), True) 
])

spark = SparkSession.builder.appName("KafkaStockStream").getOrCreate()

kafka_stream = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "stock-topic").load()

# Convert Kafka value to string and parse the JSON data
stock_data = kafka_stream.selectExpr("CAST(value AS STRING) as json_data").select(from_json("json_data", schema).alias("data")).select("data.timestamp", "data.open", "data.high", "data.low", "data.close", "data.volume")

# Write the results to the console (for real-time display)
query_console = stock_data.writeStream.outputMode("append").format("console").option("checkpointLocation", "./checkpoint_console2").start()

# Write the results to a CSV file
query_csv = stock_data.writeStream.outputMode("append").format("csv").option("path", "./output_csv2").option("checkpointLocation", "./checkpoint_csv2").start()

query_console.awaitTermination() 
query_csv.awaitTermination()     